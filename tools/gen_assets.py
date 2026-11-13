"""Collect the episode's stock assets.

Default source = "manual": you draw them in Canva / Illustrator and drop them in art/
    art/<asset_name>.png   (transparent PNG)   or   art/<asset_name>.svg
The same art/ library is reused by every episode (commit it to git).

    python tools/gen_assets.py episodes/01_communism.yaml               # use art/
    python tools/gen_assets.py episodes/01_communism.yaml --allow-missing  # placeholders for what's not drawn yet
    python tools/gen_assets.py episodes/01_communism.yaml --source recraft # AI (needs Recraft credits)
    python tools/gen_assets.py episodes/01_communism.yaml --mock          # all placeholders

It also writes art/TODO_<episode_id>.md = drawing checklist for the designer.
"""
import argparse
import hashlib
import io
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import LIB_DIR as LIB, ROOT, ep_dir, episode, load_env, need_env, read_json, series

API = "https://external.api.recraft.ai/v1/images/generations"
ART = ROOT / "art"
EXTS = (".png", ".webp", ".svg")


# ---------------- helpers ----------------
def trim(img, pad=8):
    img = img.convert("RGBA")
    bbox = img.getchannel("A").point(lambda a: 255 if a > 10 else 0).getbbox()
    if bbox:
        l, t, r, b = bbox
        img = img.crop((max(l - pad, 0), max(t - pad, 0),
                        min(r + pad, img.width), min(b + pad, img.height)))
    return img


def key_white(img, thresh=28):
    """Remove a plain white background (Canva free export) by flood-filling from the corners."""
    img = img.convert("RGBA")
    w, h = img.size
    for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        r, g, b, a = img.getpixel(xy)
        if a > 0 and min(r, g, b) > 235:
            ImageDraw.floodfill(img, xy, (0, 0, 0, 0), thresh=thresh)
    return img


def sticker(img, width=14, color=(255, 255, 255, 255)):
    """white halo around the drawing so dark outlines stay visible on the navy background."""
    img = img.convert("RGBA")
    pad = width + 4
    canvas = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(img, (pad, pad))
    a = canvas.getchannel("A").point(lambda v: 255 if v > 20 else 0)
    halo = a.filter(ImageFilter.MaxFilter(width * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
    out = Image.new("RGBA", canvas.size, color)
    out.putalpha(halo)
    out.alpha_composite(canvas)
    return out


def svg_to_png(path, height=1400):
    try:
        import cairosvg
        data = cairosvg.svg2png(url=str(path), output_height=height)
        return Image.open(io.BytesIO(data))
    except ImportError:
        out = path.with_suffix(".tmp.png")
        subprocess.run(["rsvg-convert", "-h", str(height), "-o", str(out), str(path)], check=True)
        img = Image.open(out).copy()
        out.unlink()
        return img


def load_art(path, white_bg):
    img = svg_to_png(path) if path.suffix.lower() == ".svg" else Image.open(path)
    img = img.convert("RGBA")
    if white_bg or img.getchannel("A").getextrema()[0] == 255:  # fully opaque -> probably white bg
        img = key_white(img)
    return trim(img)


def placeholder(name):
    im = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 760, 760), 80, fill=(90, 90, 110, 255), outline=(255, 209, 102, 255), width=14)
    try:
        f = ImageFont.truetype(str(ROOT / "assets/fonts/Tajawal-Black.ttf"), 100)
    except OSError:
        f = ImageFont.load_default()
    d.text((400, 400), name, font=f, fill=(255, 255, 255, 255), anchor="mm")
    return im


def find_art(name):
    for ext in EXTS:
        p = ART / f"{name}{ext}"
        if p.exists():
            return p
    return None


def write_todo(ep, missing):
    lines = [f"# رسومات حلقة {ep['id']}", "",
             "ارسم كل عنصر لوحده بخلفية شفافة واحفظه باسمه بالظبط في art/",
             "(Canva: صفحة لكل عنصر بنفس الترتيب ده — Illustrator: Artboard لكل عنصر باسمه)", "",
             "| # | الاسم (اسم الملف) | الوصف | الحالة |", "|---|---|---|---|"]
    for i, (name, desc) in enumerate(ep["assets"].items(), 1):
        lines.append(f"| {i} | `{name}` | {desc} | {'⬜ ناقص' if name in missing else '✅'} |")
    out = ART / f"TODO_{ep['id']}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


# ---------------- recraft (optional) ----------------
def recraft(prompt, cfg, style, token):
    import requests
    body = {"prompt": prompt, "model": style.get("model", cfg["assets"]["model"]),
            "style_id": style["style_id"], "size": cfg["assets"]["size"], "n": 1,
            "response_format": "url", "image_format": "png",
            "controls": {"background_color": {"rgb": [255, 255, 255]}}}
    r = requests.post(API, json=body, headers={"Authorization": f"Bearer {token}"}, timeout=180)
    if r.status_code >= 300:
        raise SystemExit(f"[x] Recraft {r.status_code}: {r.text}")
    img = requests.get(r.json()["data"][0]["url"], timeout=120).content
    return key_white(Image.open(io.BytesIO(img)))


# ---------------- main ----------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("episode")
    p.add_argument("--source", choices=["manual", "recraft"], default=None)
    p.add_argument("--allow-missing", action="store_true")
    p.add_argument("--white-bg", action="store_true", help="force white-background removal")
    p.add_argument("--only", default="")
    p.add_argument("--force", action="store_true")
    p.add_argument("--mock", action="store_true")
    a = p.parse_args()

    load_env()
    cfg, ep = series(), episode(a.episode)
    source = a.source or cfg["assets"].get("source", "manual")
    out_dir = ep_dir(ep) / "assets"
    ART.mkdir(exist_ok=True)
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    missing = []

    style = token = None
    if source == "recraft" and not a.mock:
        token = need_env("RECRAFT_API_TOKEN")
        style = read_json(ROOT / "style" / "style.json")
        LIB.mkdir(parents=True, exist_ok=True)

    for name, desc in ep["assets"].items():
        if only and name not in only:
            continue
        target = out_dir / f"{name}.png"
        if a.mock:
            placeholder(name).save(target)
            continue

        if source == "manual":
            src = find_art(name)
            if src:
                img = load_art(src, a.white_bg)
                if cfg["assets"].get("sticker", True):
                    img = sticker(img)
                img.save(target)
                print(f"[art] {name}  <- {src.relative_to(ROOT)}")
            else:
                missing.append(name)
                placeholder(name).save(target)
            continue

        # recraft
        full = f"{desc}. {cfg['assets']['prompt_suffix']}"
        h = hashlib.sha1((full + style["style_id"]).encode()).hexdigest()[:8]
        cached = LIB / f"{name}__{h}.png"
        if not cached.exists() or a.force:
            print(f"[gen] {name}")
            trim(recraft(full, cfg, style, token)).save(cached)
        shutil.copy(cached, target)

    if source == "manual" and not a.mock:
        todo = write_todo(ep, set(missing))
        if missing:
            print(f"[!] {len(missing)} missing in art/: {', '.join(missing)}")
            print(f"    checklist -> {todo.relative_to(ROOT)}")
            if not a.allow_missing:
                sys.exit("[x] Draw them (or run with --allow-missing to preview with placeholders).")
    print("[ok] assets ready in", out_dir.relative_to(ROOT))


if __name__ == "__main__":
    main()
