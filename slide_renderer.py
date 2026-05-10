"""
Pure-Python slide renderer (Pillow-based).

Renders slide_data dicts to PNG images for layout verification.
This replaces LibreOffice rendering when that tool is unavailable.
Output is a faithful geometric preview — accurate enough to catch
position, colour, size, and text-overflow issues.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

# Rendered slide canvas size (pixels)
RENDER_W = 1280
RENDER_H = 720

# Japanese-capable fonts to try in order
_FONT_PATHS = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


# ── helpers ───────────────────────────────────────────────────────────────────

def _hex_to_rgb(hex_color: str, alpha: float = 1.0) -> tuple:
    h = (hex_color or "#000000").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(alpha * 255)
    return (r, g, b, a)


def _px(pct: float) -> int:
    return int(pct / 100 * RENDER_W)


def _py(pct: float) -> int:
    return int(pct / 100 * RENDER_H)


def _load_font(size_pt: float) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    px = max(8, int(size_pt * RENDER_H / 72 / 7.5))  # pt → px at 96dpi on 7.5" slide
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, px)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def _mix_rgba(base: Image.Image, overlay_rgba: tuple, box: tuple[int, int, int, int]) -> None:
    """Alpha-composite a solid colour rectangle onto base image."""
    r, g, b, a = overlay_rgba
    if a == 0:
        return
    patch = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (r, g, b, a))
    base.paste(patch, (box[0], box[1]), patch)


# ── element renderers ─────────────────────────────────────────────────────────

def _draw_shape(canvas: Image.Image, elem: dict) -> None:
    b      = elem.get("bounds", {})
    x0, y0 = _px(b.get("x", 0)), _py(b.get("y", 0))
    x1, y1 = x0 + _px(b.get("width", 0)), y0 + _py(b.get("height", 0))
    x1, y1 = max(x0 + 1, x1), max(y0 + 1, y1)

    etype  = elem.get("element_type", "rectangle")
    fill_d = elem.get("fill") or {}
    brd_d  = elem.get("border") or {}

    # --- fill colour ---
    if fill_d.get("type") == "none" or not fill_d:
        fill_rgba = (0, 0, 0, 0)
    elif fill_d.get("type") == "gradient":
        stops = fill_d.get("gradient_stops") or []
        color = stops[0].get("color", "#888888") if stops else fill_d.get("color", "#888888")
        fill_rgba = _hex_to_rgb(color, fill_d.get("opacity", 1.0))
    else:
        fill_rgba = _hex_to_rgb(fill_d.get("color", "#888888"), fill_d.get("opacity", 1.0))

    # --- border colour ---
    if brd_d.get("visible") and brd_d.get("width_pt", 0) > 0:
        brd_rgba  = _hex_to_rgb(brd_d.get("color", "#000000"))
        brd_width = max(1, int(brd_d.get("width_pt", 1)))
    else:
        brd_rgba  = None
        brd_width = 0

    # --- draw onto RGBA working layer ---
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)

    radius = int(min(x1 - x0, y1 - y0) * elem.get("corner_radius_pct", 0) / 100)

    if etype in ("rectangle", "line", "image_placeholder"):
        draw.rectangle([x0, y0, x1, y1], fill=fill_rgba,
                       outline=brd_rgba, width=brd_width)
    elif etype == "rounded_rectangle":
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                                fill=fill_rgba, outline=brd_rgba, width=brd_width)
    elif etype == "oval":
        draw.ellipse([x0, y0, x1, y1], fill=fill_rgba,
                     outline=brd_rgba, width=brd_width)

    canvas.alpha_composite(layer)


def _wrap_text(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
               max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    lines: list[str] = []
    for raw_line in text.split("\n"):
        words = raw_line.split(" ")
        cur   = ""
        for word in words:
            test = (cur + " " + word).strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def _draw_text(canvas: Image.Image, elem: dict) -> None:
    b      = elem.get("bounds", {})
    x0, y0 = _px(b.get("x", 0)), _py(b.get("y", 0))
    x1, y1 = x0 + _px(b.get("width", 0)), y0 + _py(b.get("height", 0))

    tm  = elem.get("text_margin") or {}
    lm  = _px(tm.get("left", 2))
    rm  = _px(tm.get("right", 2))
    tm_ = _py(tm.get("top", 1))
    bm  = _py(tm.get("bottom", 1))

    inner_x0 = x0 + lm
    inner_y0 = y0 + tm_
    inner_x1 = x1 - rm
    inner_y1 = y1 - bm
    max_w    = max(1, inner_x1 - inner_x0)

    v_align  = elem.get("text_vertical_align", "top")

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)

    paragraphs = elem.get("text_content") or []

    # Pre-measure total height to handle vertical alignment
    all_lines_data: list[tuple[list[str], ImageFont.FreeTypeFont | ImageFont.ImageFont,
                               tuple, float, float]] = []
    total_h = 0
    align_map = {"left": "la", "center": "mm", "right": "ra", "centre": "mm"}

    for para in paragraphs:
        runs     = para.get("runs") or []
        ls_factor = float(para.get("line_spacing_factor", 1.2))
        sp_after  = _py(para.get("space_after_pt", 0) / 72 * RENDER_H)

        if not runs:
            total_h += int(12 * ls_factor) + sp_after
            all_lines_data.append(([], _load_font(12), (255, 255, 255, 255), ls_factor, sp_after))
            continue

        run0     = runs[0]
        font     = _load_font(run0.get("font_size_pt", 12.0))
        color    = _hex_to_rgb(run0.get("color", "#000000"))
        text_str = "".join(r.get("text", "") for r in runs)
        lines    = _wrap_text(text_str, font, max_w, draw)

        line_h   = max(1, draw.textbbox((0, 0), "あAg", font=font)[3])
        para_h   = int(line_h * ls_factor * len(lines)) + sp_after
        total_h += para_h
        all_lines_data.append((lines, font, color, ls_factor, sp_after))

    if v_align == "middle":
        cur_y = inner_y0 + max(0, (inner_y1 - inner_y0 - total_h) // 2)
    elif v_align == "bottom":
        cur_y = inner_y1 - total_h
    else:
        cur_y = inner_y0

    for (para, (lines, font, color, ls_f, sp_after)) in zip(paragraphs, all_lines_data):
        alignment = para.get("alignment", "left")
        line_h = max(1, draw.textbbox((0, 0), "あAg", font=font)[3]) if lines else 12

        for line in lines:
            if cur_y > inner_y1:
                break
            bbox = draw.textbbox((0, 0), line, font=font)
            lw   = bbox[2] - bbox[0]

            if alignment in ("center", "centre"):
                tx = inner_x0 + (max_w - lw) // 2
            elif alignment == "right":
                tx = inner_x1 - lw
            else:
                tx = inner_x0

            draw.text((tx, cur_y), line, font=font, fill=color)
            cur_y += int(line_h * ls_f)

        cur_y += sp_after

    canvas.alpha_composite(layer)


# ── public API ────────────────────────────────────────────────────────────────

def render_slide_data(slide_data: dict, output_path: str | Path) -> Path:
    """Render a slide_data dict to a PNG image using Pillow. Returns output path."""
    output_path = Path(output_path)

    canvas = Image.new("RGBA", (RENDER_W, RENDER_H), (255, 255, 255, 255))

    # Background
    bg = slide_data.get("slide_background") or {}
    if bg.get("fill_type", "solid") != "none":
        if bg.get("fill_type") == "gradient":
            stops = bg.get("gradient_stops") or []
            c = stops[0].get("color", "#FFFFFF") if stops else bg.get("color", "#FFFFFF")
        else:
            c = bg.get("color", "#FFFFFF")
        layer = Image.new("RGBA", (RENDER_W, RENDER_H), _hex_to_rgb(c))
        canvas.alpha_composite(layer)

    # Sort elements by z_order
    elements = sorted(slide_data.get("elements", []), key=lambda e: e.get("z_order", 0))

    for elem in elements:
        try:
            etype = elem.get("element_type", "rectangle")
            if etype != "text_box":
                _draw_shape(canvas, elem)
            if elem.get("text_content"):
                _draw_text(canvas, elem)
        except Exception as ex:
            print(f"  [RENDER WARN] '{elem.get('id', '?')}': {ex}")

    canvas.convert("RGB").save(str(output_path))
    return output_path
