"""Bring drawings from Canva / Illustrator into art/ with the right names.

Canva  (one page per asset, SAME ORDER as `assets:` in the episode yaml):
    Share > Download > PNG > (Transparent background if Pro) > All pages  -> a .zip
    python tools/import_art.py canva.zip --episode episodes/01_communism.yaml
    python tools/import_art.py canva.zip --episode episodes/01_communism.yaml --start 3
        (--start N = page 1 of the zip is asset number N; for adding missing ones later)

Illustrator (one artboard per asset, artboard NAME = asset name):
    File > Export > Export for Screens > Artboards, format PNG or SVG  -> a folder (or zip)
    python tools/import_art.py ~/Downloads/export_folder
"""
import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from common import ROOT, episode

ART = ROOT / "art"
IMG = (".png", ".svg", ".webp", ".jpg", ".jpeg")


def collect(src):
    src = Path(src).expanduser()
    if src.suffix.lower() == ".zip":
        tmp = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(src) as z:
            z.extractall(tmp)
        src = tmp
    files = [f for f in src.rglob("*") if f.suffix.lower() in IMG and not f.name.startswith(".")]
    if not files:
        sys.exit("[x] no images found")
    return files


def num(f):
    m = re.findall(r"\d+", f.stem)
    return int(m[-1]) if m else 0


def clean(stem):
    s = re.sub(r"@\dx$", "", stem)            # factory@2x
    s = re.sub(r"[-_ ]\d{1,2}$", "", s)        # factory-01
    return s.strip().lower().replace(" ", "_")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", help="zip or folder")
    p.add_argument("--episode", help="needed for Canva page-order mapping")
    p.add_argument("--start", type=int, default=1)
    a = p.parse_args()

    ART.mkdir(exist_ok=True)
    files = collect(a.source)

    if a.episode:  # Canva: map by page order
        names = list(episode(a.episode)["assets"].keys())[a.start - 1:]
        files = sorted(files, key=num)
        if len(files) != len(names):
            print(f"[!] {len(files)} pages vs {len(names)} assets — mapping the first {min(len(files), len(names))}")
        pairs = list(zip(names, files))
    else:          # Illustrator: map by file name
        pairs = [(clean(f.stem), f) for f in files]

    for name, f in pairs:
        dst = ART / f"{name}{'.svg' if f.suffix.lower() == '.svg' else '.png'}"
        if f.suffix.lower() in (".jpg", ".jpeg", ".webp"):
            from PIL import Image
            Image.open(f).convert("RGBA").save(dst)
        else:
            shutil.copy(f, dst)
        print(f"[ok] {f.name:30s} -> art/{dst.name}")
    print("Next: python tools/gen_assets.py <episode.yaml>")


if __name__ == "__main__":
    main()
