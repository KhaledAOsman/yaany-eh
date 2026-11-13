"""Create ONE reusable Recraft style from the reference images in style/refs/.

Run once for the whole series:
    python tools/make_style.py
It writes style/style.json -> {"style_id": "..."} which gen_assets.py uses forever.
"""
import argparse
import sys

import requests

from common import ROOT, load_env, need_env, write_json

API = "https://external.api.recraft.ai/v1/styles"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--match", default="precise", choices=["precise", "flexible"])
    p.add_argument("--model", default="recraftv4_styles")
    a = p.parse_args()

    load_env()
    token = need_env("RECRAFT_API_TOKEN")
    refs = sorted(
        f for f in (ROOT / "style" / "refs").iterdir()
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
    )
    if not refs:
        sys.exit("[x] Put 1-10 reference images in style/refs/ first.")
    refs = refs[:10]
    print(f"[i] Creating style from {len(refs)} reference image(s)...")

    files = [("files", (f.name, f.open("rb"))) for f in refs]
    r = requests.post(
        API,
        headers={"Authorization": f"Bearer {token}"},
        data={"model": a.model, "match": a.match},
        files=files,
        timeout=120,
    )
    if r.status_code >= 300:
        sys.exit(f"[x] Recraft error {r.status_code}: {r.text}")
    style_id = r.json()["id"]
    write_json(ROOT / "style" / "style.json", {"style_id": style_id, "model": a.model})
    print(f"[ok] style_id = {style_id}  -> saved to style/style.json")


if __name__ == "__main__":
    main()
