"""Generate the series sound-effect library once (ElevenLabs Sound Effects) -> sfx/<name>.mp3

    python tools/gen_sfx.py            # generate missing ones
    python tools/gen_sfx.py --force    # regenerate all
    python tools/gen_sfx.py --mock     # synthetic beeps with ffmpeg (no API)
"""
import argparse
import subprocess

import requests

from common import ROOT, SFX_DIR, load_env, load_yaml, need_env

API = "https://api.elevenlabs.io/v1/sound-generation"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    p.add_argument("--mock", action="store_true")
    a = p.parse_args()

    load_env()
    lib = load_yaml(ROOT / "config" / "sfx.yaml")
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    key = "" if a.mock else need_env("ELEVENLABS_API_KEY")

    for i, (name, spec) in enumerate(lib.items()):
        out = SFX_DIR / f"{name}.mp3"
        if out.exists() and not a.force:
            print(f"[cache] {name}")
            continue
        print(f"[sfx] {name}")
        if a.mock:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                            f"sine=frequency={220 + i * 90}:sample_rate=44100",
                            "-t", str(min(spec["duration"], 0.4)), "-af", "afade=t=out:st=0.05:d=0.35,volume=0.4",
                            str(out)], check=True)
            continue
        r = requests.post(API, params={"output_format": "mp3_44100_128"},
                          headers={"xi-api-key": key},
                          json={"text": spec["prompt"], "duration_seconds": spec["duration"],
                                "prompt_influence": spec.get("influence", 0.6)},
                          timeout=180)
        if r.status_code >= 300:
            raise SystemExit(f"[x] ElevenLabs {r.status_code}: {r.text}")
        out.write_bytes(r.content)
    print("[ok] sfx library in", SFX_DIR)


if __name__ == "__main__":
    main()
