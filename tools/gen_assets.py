"""Generate the episode's stock assets with Recraft (same style every time).

    python tools/gen_assets.py episodes/02_communism.yaml
    python tools/gen_assets.py episodes/02_communism.yaml --only factory,coins --force
    python tools/gen_assets.py episodes/02_communism.yaml --variants 3   # pick the best manually
    python tools/gen_assets.py episodes/02_communism.yaml --mock         # placeholders, no API

Every asset is cached in library/<name>__<hash>.png so the same prompt is never paid twice,
and can be reused across episodes (commit library/ to git).
"""
import argparse
import hashlib
import io
import shutil
import sys

import requests
from PIL import Image, ImageDraw, ImageFont

from common import LIB_DIR as LIB, ROOT, ep_dir, episode, load_env, need_env, read_json, series

API = "https://external.api.recraft.ai/v1/images/generations"

_rembg_session = None


def remove_bg(img):
    global _rembg_session
    from rembg import new_session, remove  # lazy import (heavy)

    if _rembg_session is None:
        _rembg_session = new_session("isnet-general-use")
    return remove(img, session=_rembg_session)


def trim(img, pad=8):
    img = img.convert("RGBA")
    bbox = img.getchannel("A").point(lambda a: 255 if a > 10 else 0).getbbox()
    if bbox:
        l, t, r, b = bbox
        img = img.crop((max(l - pad, 0), max(t - pad, 0),
                        min(r + pad, img.width), min(b + pad, img.height)))
    return img


def mock_image(name, idx=0):
    colors = [(76, 175, 80), (255, 209, 102), (230, 57, 70), (69, 123, 157), (240, 240, 240)]
    c = colors[(sum(map(ord, name)) + idx) % len(colors)]
    im = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 760, 760), 80, fill=c + (255,), outline=(20, 20, 20, 255), width=18)
    try:
        f = ImageFont.truetype(str(ROOT / "assets/fonts/Tajawal-Black.ttf"), 110)
    except OSError:
        f = ImageFont.load_default()
    d.text((400, 400), name, font=f, fill=(20, 20, 20, 255), anchor="mm")
    return im


def recraft(prompt, cfg, style, token, n):
    body = {
        "prompt": prompt,
        "model": style.get("model", cfg["assets"]["model"]),
        "style_id": style["style_id"],
        "size": cfg["assets"]["size"],
        "n": n,
        "response_format": "url",
        "image_format": "png",
        "controls": {"background_color": {"rgb": [255, 255, 255]}},
    }
    r = requests.post(API, json=body, headers={"Authorization": f"Bearer {token}"}, timeout=180)
    if r.status_code >= 300:
        raise RuntimeError(f"Recraft {r.status_code}: {r.text}")
    out = []
    for item in r.json()["data"]:
        img = requests.get(item["url"], timeout=120).content  # URLs expire (~24h) -> download now
        out.append(Image.open(io.BytesIO(img)).convert("RGBA"))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("episode")
    p.add_argument("--only", default="", help="comma separated asset names")
    p.add_argument("--force", action="store_true", help="regenerate even if cached")
    p.add_argument("--variants", type=int, default=1)
    p.add_argument("--mock", action="store_true")
    a = p.parse_args()

    load_env()
    cfg, ep = series(), episode(a.episode)
    out_dir = ep_dir(ep) / "assets"
    LIB.mkdir(parents=True, exist_ok=True)
    only = {s.strip() for s in a.only.split(",") if s.strip()}

    style, token = {}, ""
    if not a.mock:
        token = need_env("RECRAFT_API_TOKEN")
        sf = ROOT / "style" / "style.json"
        if not sf.exists():
            sys.exit("[x] style/style.json not found. Run: python tools/make_style.py")
        style = read_json(sf)

    for name, prompt in ep["assets"].items():
        if only and name not in only:
            continue
        full_prompt = f"{prompt}. {cfg['assets']['prompt_suffix']}"
        h = hashlib.sha1((full_prompt + str(style.get("style_id"))).encode()).hexdigest()[:8]
        cached = LIB / f"{name}__{'mock' if a.mock else h}.png"
        target = out_dir / f"{name}.png"

        if cached.exists() and not a.force:
            shutil.copy(cached, target)
            print(f"[cache] {name}")
            continue

        print(f"[gen] {name}: {prompt}")
        imgs = [mock_image(name)] if a.mock else recraft(full_prompt, cfg, style, token, a.variants)
        for i, img in enumerate(imgs):
            if cfg["assets"].get("remove_background") and not a.mock:
                img = remove_bg(img)
            img = trim(img)
            if i == 0:
                img.save(cached)
                shutil.copy(cached, target)
            else:  # extra variants for manual picking
                img.save(out_dir / f"{name}__v{i + 1}.png")
        print(f"   -> {target.relative_to(ROOT)}")

    print("[ok] assets ready in", out_dir.relative_to(ROOT))


if __name__ == "__main__":
    main()
