#!/usr/bin/env python3
"""
Image to PPTX Converter
-----------------------
Converts a slide image to an editable PowerPoint (.pptx) file.

Workflow
  1. Analyze  — Claude Vision extracts every element + its layout/style
  2. Build    — python-pptx assembles the editable PPTX (no SVG, no full-slide screenshot)
  3. Render   — Pillow renders slide_data for visual verification (LibreOffice fallback)
  4. Compare  — pixel similarity is computed vs the original image
  5. Fix loop — Claude recommends targeted fixes; the cycle repeats until the quality
                threshold is met or the iteration limit is reached
  6. Deliver  — final PPTX + rendered PNG are reported

Usage
  export ANTHROPIC_API_KEY=sk-ant-...
  python image_to_pptx.py  input.png
  python image_to_pptx.py  input.png  --output deck.pptx  --max-iter 3  --threshold 0.78
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

from pptx_builder import build_pptx
from slide_analyzer import analyze_slide, get_fixes
from slide_renderer import render_slide_data


# ── rendering ─────────────────────────────────────────────────────────────────

def _try_libreoffice(pptx_path: Path, out_dir: Path) -> Path | None:
    """Attempt LibreOffice rendering; return PNG path or None on failure."""
    try:
        tmp = out_dir / pptx_path.name
        if tmp.resolve() != pptx_path.resolve():
            shutil.copy2(pptx_path, tmp)
        before = {p.stat().st_mtime for p in out_dir.glob("*.png")}
        r = subprocess.run(
            ["soffice", "--headless", "--norestore", "--convert-to", "png",
             "--outdir", str(out_dir), str(tmp)],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            return None
        new = [p for p in out_dir.glob("*.png") if p.stat().st_mtime not in before]
        return sorted(new, key=lambda p: p.stat().st_mtime, reverse=True)[0] if new else None
    except Exception:
        return None


def render_slide(slide_data: dict, out_dir: Path, pptx_path: Path, label: str = "render") -> Path:
    """Render the slide as PNG.  Tries LibreOffice first, falls back to Pillow."""
    out_dir.mkdir(parents=True, exist_ok=True)
    lo_result = _try_libreoffice(pptx_path, out_dir)
    if lo_result:
        print("          (rendered via LibreOffice)")
        return lo_result
    # Pillow-based renderer
    out_png = out_dir / f"{label}.png"
    render_slide_data(slide_data, out_png)
    print("          (rendered via Pillow — geometric preview)")
    return out_png


# ── comparison ────────────────────────────────────────────────────────────────

_CMP_SIZE = (1280, 720)


def compute_similarity(p1: Path, p2: Path) -> float:
    """Return pixel similarity in [0.0, 1.0] between two images."""
    img1 = Image.open(p1).convert("RGB").resize(_CMP_SIZE, Image.LANCZOS)
    img2 = Image.open(p2).convert("RGB").resize(_CMP_SIZE, Image.LANCZOS)
    diff = ImageChops.difference(img1, img2)
    hist = diff.histogram()
    total_diff = sum(i * cnt for i, cnt in enumerate(hist))
    max_diff   = 255 * 3 * _CMP_SIZE[0] * _CMP_SIZE[1]
    return max(0.0, 1.0 - total_diff / max_diff)


def save_comparison(orig: Path, rendered: Path, out: Path) -> None:
    """Save a side-by-side comparison PNG (original left, rendered right)."""
    half = (_CMP_SIZE[0] // 2, _CMP_SIZE[1] // 2)
    img1 = Image.open(orig).convert("RGB").resize(half, Image.LANCZOS)
    img2 = Image.open(rendered).convert("RGB").resize(half, Image.LANCZOS)
    cmp  = Image.new("RGB", (_CMP_SIZE[0], half[1]))
    cmp.paste(img1, (0, 0))
    cmp.paste(img2, (half[0], 0))
    cmp.save(out)


# ── fix application ───────────────────────────────────────────────────────────

def _apply_fix(slide_data: dict, fix: dict) -> None:
    """Apply a single dot-notation fix to the in-memory slide_data dict."""
    eid   = fix.get("element_id")
    path  = fix.get("property_path", "")
    value = fix.get("new_value")
    if not eid or not path or value is None:
        return

    target = next((e for e in slide_data.get("elements", []) if e.get("id") == eid), None)
    if target is None:
        return

    parts = path.split(".")
    obj = target
    for part in parts[:-1]:
        if isinstance(obj, dict):
            obj = obj.setdefault(part, {})
        elif isinstance(obj, list) and part.isdigit():
            idx = int(part)
            obj = obj[idx] if idx < len(obj) else {}
        else:
            return

    if isinstance(obj, dict):
        obj[parts[-1]] = value


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Convert a slide image to an editable PPTX using Claude Vision.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Set ANTHROPIC_API_KEY before running.",
    )
    ap.add_argument("image",        help="Input slide image (PNG / JPEG)")
    ap.add_argument("--output","-o",help="Output PPTX path  (default: <image>.pptx)")
    ap.add_argument("--max-iter",   type=int,   default=2,    help="Max fix iterations (default 2)")
    ap.add_argument("--threshold",  type=float, default=0.75, help="Similarity threshold 0–1 (default 0.75)")
    ap.add_argument("--save-json",  action="store_true",      help="Save analysis JSON alongside PPTX")
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ERROR: ANTHROPIC_API_KEY is not set.")

    image_path = Path(args.image)
    if not image_path.exists():
        sys.exit(f"ERROR: File not found: {image_path}")

    out_pptx   = Path(args.output) if args.output else image_path.with_suffix(".pptx")
    render_dir = image_path.parent / f"{image_path.stem}_renders"

    _hr = "=" * 60
    print(f"\n{_hr}\nImage → PPTX Converter\n{_hr}")
    print(f"  Input     : {image_path}")
    print(f"  Output    : {out_pptx}")
    print(f"  Render dir: {render_dir}")
    print()

    # ── Step 1: Analyze ──────────────────────────────────────────────────────
    print("Step 1/6  Analyzing image with Claude Vision …")
    slide_data = analyze_slide(image_path)
    n_elem = len(slide_data.get("elements", []))
    print(f"          {n_elem} elements detected")

    if args.save_json:
        jpath = out_pptx.with_suffix(".analysis.json")
        jpath.write_text(json.dumps(slide_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"          JSON saved → {jpath}")

    # ── Step 2: Build PPTX ───────────────────────────────────────────────────
    print("\nStep 2/6  Building PPTX …")
    build_pptx(slide_data, out_pptx)
    print(f"          Saved → {out_pptx}")

    # ── Step 3: Render ───────────────────────────────────────────────────────
    print("\nStep 3/6  Rendering slide …")
    rendered = render_slide(slide_data, render_dir, out_pptx, label="render_0")
    print(f"          Rendered → {rendered}")

    # ── Step 4: Compare ──────────────────────────────────────────────────────
    print("\nStep 4/6  Comparing images …")
    similarity = compute_similarity(image_path, rendered)
    cmp_path   = render_dir / "comparison_0.png"
    save_comparison(image_path, rendered, cmp_path)
    print(f"          Similarity : {similarity:.1%}")
    print(f"          Comparison → {cmp_path}")

    # ── Step 5: Fix loop ─────────────────────────────────────────────────────
    for i in range(args.max_iter):
        if similarity >= args.threshold:
            print(f"\nQuality threshold reached ({similarity:.1%} ≥ {args.threshold:.1%}) — skipping fixes.")
            break

        print(f"\nStep 5/6  Fix iteration {i+1}/{args.max_iter} …")
        try:
            fixes = get_fixes(image_path, rendered, slide_data)
        except Exception as ex:
            print(f"          Fix analysis failed: {ex}")
            break

        if not fixes:
            print("          No fixes recommended — stopping.")
            break

        print(f"          {len(fixes)} fix(es):")
        for fx in fixes:
            print(f"            [{fx.get('element_id','?')}] {fx.get('property_path','?')} "
                  f"→ {fx.get('new_value','?')}  ({fx.get('reason','')})")
            _apply_fix(slide_data, fx)

        build_pptx(slide_data, out_pptx)
        rendered   = render_slide(slide_data, render_dir, out_pptx, label=f"render_{i+1}")
        new_sim    = compute_similarity(image_path, rendered)
        cmp_path   = render_dir / f"comparison_{i+1}.png"
        save_comparison(image_path, rendered, cmp_path)
        print(f"          Similarity : {similarity:.1%} → {new_sim:.1%}")
        print(f"          Comparison → {cmp_path}")
        similarity = new_sim

    # ── Step 6: Final verification ───────────────────────────────────────────
    print(f"\nStep 6/6  Final verification …")

    # Quality verdict
    if similarity >= args.threshold:
        verdict = f"PASS  ({similarity:.1%} ≥ {args.threshold:.1%})"
    elif similarity >= 0.55:
        verdict = f"WARN  ({similarity:.1%} — review comparison images)"
    else:
        verdict = f"FAIL  ({similarity:.1%} — significant differences remain)"

    print(f"\n{_hr}")
    print(f"  Result     : {verdict}")
    print(f"  PPTX       : {out_pptx}")
    print(f"  PNG render : {rendered}")
    print(f"  Comparisons: {render_dir}/comparison_*.png")
    print(f"{_hr}\n")

    # SVG check
    import zipfile
    try:
        with zipfile.ZipFile(out_pptx) as z:
            svgs = [n for n in z.namelist() if n.endswith(".svg")]
        if svgs:
            print(f"WARNING: SVG files found in PPTX: {svgs}")
        else:
            print("SVG check: PASS (no .svg files in pptx)")
    except Exception:
        pass


if __name__ == "__main__":
    main()
