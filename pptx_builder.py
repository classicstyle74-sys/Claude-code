"""Build an editable PPTX from structured slide data produced by slide_analyzer."""

from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

SLIDE_W_IN = 13.333
SLIDE_H_IN = 7.5
SLIDE_W_EMU = Inches(SLIDE_W_IN)   # 12,192,000
SLIDE_H_EMU = Inches(SLIDE_H_IN)   # 6,858,000

_SHP_RECT   = 1   # MSO_AUTO_SHAPE_TYPE.RECTANGLE
_SHP_ROUND  = 5   # MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE
_SHP_OVAL   = 9   # MSO_AUTO_SHAPE_TYPE.OVAL


# ── helpers ──────────────────────────────────────────────────────────────────

def _px(pct: float) -> Emu:
    return Emu(max(1, int(pct / 100 * SLIDE_W_EMU)))

def _py(pct: float) -> Emu:
    return Emu(max(1, int(pct / 100 * SLIDE_H_EMU)))

def _rgb(hex_color: str) -> RGBColor:
    h = (hex_color or "#000000").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return RGBColor(r, g, b)

def _hex_val(hex_color: str) -> str:
    return (hex_color or "#000000").lstrip("#").upper()


# ── fill / border ─────────────────────────────────────────────────────────────

def _apply_fill(shape, fill: dict | None) -> None:
    if not fill or fill.get("type") == "none":
        shape.fill.background()
        return

    if fill.get("type") == "gradient":
        stops = fill.get("gradient_stops") or []
        if len(stops) >= 2:
            try:
                shape.fill.gradient()
                gsLst = shape.fill._fill.find(qn("a:gsLst"))
                if gsLst is not None:
                    for gs in list(gsLst):
                        gsLst.remove(gs)
                    for stop in stops:
                        gs = etree.SubElement(gsLst, qn("a:gs"))
                        gs.set("pos", str(int(stop.get("position", 0) * 100000)))
                        sf = etree.SubElement(gs, qn("a:srgbClr"))
                        sf.set("val", _hex_val(stop.get("color", "#000000")))
                ang = fill.get("gradient_angle_deg", 90)
                lin = shape.fill._fill.find(qn("a:lin"))
                if lin is not None:
                    lin.set("ang", str(int(ang * 60000)))
                return
            except Exception:
                pass
        # fallback: use first stop color as solid
        color = stops[0].get("color", fill.get("color", "#000000")) if stops else fill.get("color", "#000000")
        shape.fill.solid()
        shape.fill.fore_color.rgb = _rgb(color)
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = _rgb(fill.get("color", "#000000"))

    # opacity
    opacity = float(fill.get("opacity", 1.0))
    if opacity < 1.0:
        try:
            spPr = shape._element.spPr
            sf = spPr.find(f".//{qn('a:solidFill')}")
            if sf is not None:
                clr = sf.find(qn("a:srgbClr"))
                if clr is None:
                    clr = sf.find(qn("a:sysClr"))
                if clr is not None:
                    alpha = etree.SubElement(clr, qn("a:alpha"))
                    alpha.set("val", str(int(opacity * 100000)))
        except Exception:
            pass


def _apply_border(shape, border: dict | None) -> None:
    spPr = shape._element.spPr
    ln = spPr.find(qn("a:ln"))
    if ln is None:
        ln = etree.SubElement(spPr, qn("a:ln"))
    for child in list(ln):
        ln.remove(child)

    if not border or not border.get("visible", False):
        etree.SubElement(ln, qn("a:noFill"))
        return

    color = border.get("color", "#000000")
    width_pt = float(border.get("width_pt", 1.0))
    ln.set("w", str(int(Pt(width_pt))))
    sf = etree.SubElement(ln, qn("a:solidFill"))
    clr = etree.SubElement(sf, qn("a:srgbClr"))
    clr.set("val", _hex_val(color))


def _apply_corner_radius(shape, radius_pct: float) -> None:
    if radius_pct <= 0:
        return
    try:
        spPr = shape._element.spPr
        pg = spPr.find(qn("a:prstGeom"))
        if pg is None:
            return
        avLst = pg.find(qn("a:avLst"))
        if avLst is None:
            avLst = etree.SubElement(pg, qn("a:avLst"))
        for gd in avLst.findall(qn("a:gd")):
            avLst.remove(gd)
        gd = etree.SubElement(avLst, qn("a:gd"))
        gd.set("name", "adj")
        gd.set("fmla", f"val {int(min(radius_pct, 50) * 1000)}")
    except Exception:
        pass


# ── text ──────────────────────────────────────────────────────────────────────

def _apply_text(tf, text_content: list, text_margin: dict | None, v_align: str) -> None:
    txBody = tf._txBody

    # bodyPr settings
    bodyPr = txBody.find(qn("a:bodyPr"))
    if bodyPr is None:
        bodyPr = etree.SubElement(txBody, qn("a:bodyPr"))
    va_map = {"top": "t", "middle": "ctr", "bottom": "b"}
    bodyPr.set("anchor", va_map.get(v_align, "t"))
    bodyPr.set("wrap", "square")
    bodyPr.set("rtlCol", "0")

    if text_margin:
        lm = max(0, int(text_margin.get("left", 2) / 100 * SLIDE_W_EMU))
        rm = max(0, int(text_margin.get("right", 2) / 100 * SLIDE_W_EMU))
        tm = max(0, int(text_margin.get("top", 1) / 100 * SLIDE_H_EMU))
        bm = max(0, int(text_margin.get("bottom", 1) / 100 * SLIDE_H_EMU))
        bodyPr.set("lIns", str(lm))
        bodyPr.set("rIns", str(rm))
        bodyPr.set("tIns", str(tm))
        bodyPr.set("bIns", str(bm))

    # Remove existing paragraphs
    for p in txBody.findall(qn("a:p")):
        txBody.remove(p)

    if not text_content:
        etree.SubElement(txBody, qn("a:p"))
        return

    align_map = {"left": "l", "center": "ctr", "right": "r", "justify": "just"}

    for para_data in text_content:
        p = etree.SubElement(txBody, qn("a:p"))
        pPr = etree.SubElement(p, qn("a:pPr"))

        pPr.set("algn", align_map.get(para_data.get("alignment", "left"), "l"))

        ls = float(para_data.get("line_spacing_factor", 1.0))
        if ls != 1.0:
            lnSpc = etree.SubElement(pPr, qn("a:lnSpc"))
            spcPct = etree.SubElement(lnSpc, qn("a:spcPct"))
            spcPct.set("val", str(int(ls * 100000)))

        sb = para_data.get("space_before_pt", 0)
        if sb:
            spcBef = etree.SubElement(pPr, qn("a:spcBef"))
            etree.SubElement(spcBef, qn("a:spcPts")).set("val", str(int(sb * 100)))

        sa = para_data.get("space_after_pt", 0)
        if sa:
            spcAft = etree.SubElement(pPr, qn("a:spcAft"))
            etree.SubElement(spcAft, qn("a:spcPts")).set("val", str(int(sa * 100)))

        bc = para_data.get("bullet_char")
        if bc:
            bChar = etree.SubElement(pPr, qn("a:buChar"))
            bChar.set("char", bc)
        else:
            etree.SubElement(pPr, qn("a:buNone"))

        for run_data in para_data.get("runs", []):
            r = etree.SubElement(p, qn("a:r"))
            rPr = etree.SubElement(r, qn("a:rPr"))
            rPr.set("lang", "ja-JP")
            rPr.set("altLang", "en-US")
            rPr.set("dirty", "0")

            fs = float(run_data.get("font_size_pt", 12.0))
            rPr.set("sz", str(int(fs * 100)))

            if run_data.get("bold"):   rPr.set("b", "1")
            if run_data.get("italic"): rPr.set("i", "1")
            if run_data.get("underline"): rPr.set("u", "sng")

            sf = etree.SubElement(rPr, qn("a:solidFill"))
            etree.SubElement(sf, qn("a:srgbClr")).set("val", _hex_val(run_data.get("color", "#000000")))

            fn = run_data.get("font_name") or "IPAGothic"
            for tag in (qn("a:latin"), qn("a:ea"), qn("a:cs")):
                etree.SubElement(rPr, tag).set("typeface", fn)

            etree.SubElement(r, qn("a:t")).text = run_data.get("text", "")


# ── element builder ───────────────────────────────────────────────────────────

def _build_element(slide, elem: dict) -> None:
    b = elem.get("bounds", {})
    x, y = _px(b.get("x", 0)), _py(b.get("y", 0))
    w, h = _px(b.get("width", 10)), _py(b.get("height", 10))

    etype        = elem.get("element_type", "rectangle")
    fill         = elem.get("fill") or {}
    border       = elem.get("border") or {}
    text_content = elem.get("text_content") or []
    t_margin     = elem.get("text_margin") or {}
    v_align      = elem.get("text_vertical_align", "top")
    r_pct        = float(elem.get("corner_radius_pct", 0.0))

    if etype == "text_box":
        txBox = slide.shapes.add_textbox(x, y, w, h)
        _apply_text(txBox.text_frame, text_content, t_margin, v_align)
        return

    if etype == "line":
        shape = slide.shapes.add_shape(_SHP_RECT, x, y, w, h)
        line_fill = fill if fill.get("color") else {"type": "solid", "color": "#000000"}
        _apply_fill(shape, line_fill)
        _apply_border(shape, {"visible": False})
        return

    if etype == "image_placeholder":
        shape = slide.shapes.add_shape(_SHP_RECT, x, y, w, h)
        _apply_fill(shape, fill or {"type": "solid", "color": "#CCCCCC"})
        _apply_border(shape, {"visible": False})
        desc = elem.get("image_description") or ""
        if desc:
            tf = shape.text_frame
            _apply_text(tf, [{
                "paragraph_index": 0,
                "runs": [{"text": f"[{desc[:40]}]", "font_name": "IPAGothic",
                          "font_size_pt": 7.0, "bold": False, "italic": False,
                          "underline": False, "color": "#666666"}],
                "alignment": "center", "line_spacing_factor": 1.0,
                "space_before_pt": 0, "space_after_pt": 0, "bullet_char": None,
            }], {}, "middle")
        return

    shape_type = {"rounded_rectangle": _SHP_ROUND, "oval": _SHP_OVAL}.get(etype, _SHP_RECT)
    shape = slide.shapes.add_shape(shape_type, x, y, w, h)
    _apply_fill(shape, fill)
    _apply_border(shape, border)

    if etype == "rounded_rectangle" and r_pct > 0:
        _apply_corner_radius(shape, r_pct)

    if text_content:
        _apply_text(shape.text_frame, text_content, t_margin, v_align)


# ── public entry point ────────────────────────────────────────────────────────

def build_pptx(slide_data: dict, output_path: str | Path) -> Path:
    """Build an editable PPTX from slide_data and save to output_path."""
    output_path = Path(output_path)

    prs = Presentation()
    prs.slide_width  = SLIDE_W_EMU
    prs.slide_height = SLIDE_H_EMU

    layouts = prs.slide_layouts
    blank = layouts[6] if len(layouts) > 6 else layouts[-1]
    slide = prs.slides.add_slide(blank)

    # Remove placeholder shapes inherited from layout
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)

    # Background
    bg = slide_data.get("slide_background") or {}
    if bg.get("fill_type", "solid") != "none":
        bg_shape = slide.shapes.add_shape(_SHP_RECT, Emu(0), Emu(0), SLIDE_W_EMU, SLIDE_H_EMU)
        if bg.get("fill_type") == "gradient" and bg.get("gradient_stops"):
            _apply_fill(bg_shape, {
                "type": "gradient",
                "gradient_stops": bg["gradient_stops"],
                "gradient_angle_deg": bg.get("gradient_angle_deg", 90),
            })
        else:
            _apply_fill(bg_shape, {"type": "solid", "color": bg.get("color", "#FFFFFF")})
        _apply_border(bg_shape, {"visible": False})
        # Push background shape to bottom of stack
        sp_tree = slide.shapes._spTree
        sp = bg_shape._element
        sp_tree.remove(sp)
        sp_tree.insert(2, sp)  # index 2 = after spTree header elements

    # Content elements (sorted by z_order)
    for elem in sorted(slide_data.get("elements", []), key=lambda e: e.get("z_order", 0)):
        try:
            _build_element(slide, elem)
        except Exception as ex:
            print(f"  [WARN] element '{elem.get('id', '?')}' skipped: {ex}")

    prs.save(str(output_path))
    return output_path
