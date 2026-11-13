"""Render Arabic text to transparent PNG (Blender can't shape Arabic, so text = images)."""
from PIL import Image, ImageDraw, ImageFont, features

from common import ROOT, hex_rgb

RAQM = features.check("raqm")


def _shape(text):
    if RAQM:
        return text
    import arabic_reshaper
    from bidi.algorithm import get_display
    return get_display(arabic_reshaper.reshape(text))


def render_text(text, out_path, font, size, fill="#FFFFFF", stroke=0, stroke_fill="#000000",
                pill=None, pad=(36, 18)):
    """pill = hex color -> rounded background box (used for the series badge)."""
    f = ImageFont.truetype(str(ROOT / font), size)
    kw = {"direction": "rtl", "language": "ar"} if RAQM else {}
    t = _shape(text)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l, tp, r, b = tmp.textbbox((0, 0), t, font=f, stroke_width=stroke, **kw)
    w, h = r - l, b - tp
    px, py = pad if pill else (stroke + 6, stroke + 6)
    img = Image.new("RGBA", (w + 2 * px, h + 2 * py), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if pill:
        d.rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius=img.height // 2,
                            fill=hex_rgb(pill) + (235,))
    d.text((px - l, py - tp), t, font=f, fill=hex_rgb(fill) + (255,),
           stroke_width=stroke, stroke_fill=hex_rgb(stroke_fill) + (255,), **kw)
    img.save(out_path)
    return img.size
