"""Claude Vision API slide analysis and fix recommendation."""

import base64
import json
import re
from pathlib import Path

import anthropic

ANALYSIS_SYSTEM = (
    "You are a PowerPoint slide structure analyzer. "
    "Analyze slide images and return complete structure as JSON. "
    "Return ONLY valid JSON — no markdown, no explanation, just the JSON object."
)

ANALYSIS_PROMPT = """Analyze this PowerPoint slide image and extract its complete structure.

**Slide size**: 13.333 × 7.5 inches (16:9 widescreen)

**Coordinate system** — all numeric values are PERCENTAGES (0–100):
- bounds.x  : 0 = left edge, 100 = right edge
- bounds.y  : 0 = top edge,  100 = bottom edge
- bounds.width / bounds.height : as % of slide width / height

**Rules**:
1. Identify EVERY visible element, ordered back-to-front (z_order increases toward viewer)
2. Reproduce ALL text EXACTLY — every character, space, punctuation, line-break (use \\n)
3. Estimate hex colors precisely (#RRGGBB)
4. Measure positions carefully relative to the full slide
5. Japanese/CJK text: reproduce every character exactly; use "IPAGothic" as default font name
6. For gradient fills, list 2+ color stops with their positions (0.0–1.0)

**element_type values**:
- "rectangle"         : rectangular shape
- "rounded_rectangle" : rectangle with rounded corners (set corner_radius_pct > 0)
- "oval"              : ellipse / circle
- "line"              : thin horizontal or vertical rule
- "text_box"          : text with transparent/no background
- "image_placeholder" : icon or decorative image (cannot reproduce exactly)

Return exactly this JSON schema (all keys required):

{
  "slide_background": {
    "fill_type": "solid",
    "color": "#FFFFFF",
    "gradient_stops": null,
    "gradient_angle_deg": 90
  },
  "elements": [
    {
      "id": "elem_001",
      "label": "background_rect",
      "element_type": "rectangle",
      "bounds": {"x": 0.0, "y": 0.0, "width": 100.0, "height": 100.0},
      "z_order": 0,
      "fill": {
        "type": "solid",
        "color": "#1A3557",
        "opacity": 1.0,
        "gradient_stops": null,
        "gradient_angle_deg": null
      },
      "border": {"visible": false, "color": "#000000", "width_pt": 0.0},
      "corner_radius_pct": 0.0,
      "text_content": [],
      "text_vertical_align": "top",
      "text_margin": {"left": 2.0, "top": 1.0, "right": 2.0, "bottom": 1.0},
      "image_description": null
    }
  ]
}

For elements with text, each item in text_content uses:
{
  "paragraph_index": 0,
  "runs": [
    {
      "text": "Exact text here",
      "font_name": "IPAGothic",
      "font_size_pt": 24.0,
      "bold": false,
      "italic": false,
      "underline": false,
      "color": "#FFFFFF"
    }
  ],
  "alignment": "left",
  "line_spacing_factor": 1.2,
  "space_before_pt": 0,
  "space_after_pt": 0,
  "bullet_char": null
}"""

FIX_PROMPT = """I am reproducing a PowerPoint slide. You will see two images:
1. The ORIGINAL slide (first image)
2. My CURRENT REPRODUCTION (second image)

Identify specific differences and return a JSON array of fixes.
Each fix targets a property of a specific element using dot-notation.

Return format:
[
  {
    "element_id": "elem_001",
    "property_path": "bounds.y",
    "new_value": 15.0,
    "reason": "Title starts lower in original"
  }
]

Focus on the most impactful differences:
- Position offsets  (bounds.x / bounds.y / bounds.width / bounds.height)
- Color differences (fill.color)
- Font size         (first matching run's font_size_pt — use path "text_content.0.runs.0.font_size_pt")
- Obvious missing layout issues

Return [] if differences are minor. Return ONLY the JSON array."""


def _load_b64(path: Path) -> tuple[str, str]:
    media = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    mt = media.get(path.suffix.lower(), "image/png")
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode(), mt


def _parse_json(text: str):
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    text = re.sub(r"```\s*$", "", text).strip()
    for pat in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
        m = re.search(pat, text)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return json.loads(text)


def analyze_slide(image_path: Path) -> dict:
    """Send slide image to Claude and return structured slide data dict."""
    client = anthropic.Anthropic()
    img_data, media_type = _load_b64(image_path)

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=ANALYSIS_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_data}},
                {"type": "text", "text": ANALYSIS_PROMPT},
            ],
        }],
    )
    return _parse_json(resp.content[0].text)


def get_fixes(original: Path, rendered: Path, slide_data: dict) -> list[dict]:
    """Compare original vs rendered image; return list of fix dicts."""
    client = anthropic.Anthropic()
    orig_data, orig_mt = _load_b64(original)
    rend_data, rend_mt = _load_b64(rendered)

    ids = [e.get("id", "?") for e in slide_data.get("elements", [])]
    ctx = f"\n\nAvailable element IDs: {', '.join(ids)}"

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": orig_mt, "data": orig_data}},
                {"type": "image", "source": {"type": "base64", "media_type": rend_mt, "data": rend_data}},
                {"type": "text", "text": FIX_PROMPT + ctx},
            ],
        }],
    )
    result = _parse_json(resp.content[0].text)
    return result if isinstance(result, list) else []
