"""Voice-over per scene with ElevenLabs + character timestamps (used for cues & captions).

    python tools/gen_voice.py episodes/02_communism.yaml
    python tools/gen_voice.py episodes/02_communism.yaml --only story --force
    python tools/gen_voice.py episodes/02_communism.yaml --mock   # silent audio, fake timings
"""
import argparse
import base64
import hashlib
import json
import os
import subprocess

import requests

from common import ep_dir, episode, load_env, need_env, series, write_json, read_json

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"


def scene_list(ep):
    items = [(s["id"], s.get("vo", "")) for s in ep["scenes"]]
    if ep.get("teaser", {}).get("vo"):
        items.append(("teaser", ep["teaser"]["vo"]))
    return [(i, t) for i, t in items if t.strip()]


def probe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)])
    return float(out.strip())


def mock_tts(text, mp3):
    dur = max(1.2, len(text) * 0.062)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "sine=frequency=180:sample_rate=44100", "-t", f"{dur:.2f}",
                    "-af", "volume=0.05", str(mp3)], check=True)
    step = dur / max(len(text), 1)
    return {
        "characters": list(text),
        "character_start_times_seconds": [i * step for i in range(len(text))],
        "character_end_times_seconds": [(i + 1) * step for i in range(len(text))],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("episode")
    p.add_argument("--only", default="")
    p.add_argument("--force", action="store_true")
    p.add_argument("--mock", action="store_true")
    a = p.parse_args()

    load_env()
    cfg, ep = series(), episode(a.episode)
    vdir = ep_dir(ep) / "voice"
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    vcfg = cfg["voice"]

    key = voice_id = ""
    if not a.mock:
        key = need_env("ELEVENLABS_API_KEY")
        voice_id = os.environ.get("ELEVENLABS_VOICE_ID") or vcfg.get("voice_id") or need_env("ELEVENLABS_VOICE_ID")

    items = scene_list(ep)
    for idx, (sid, text) in enumerate(items):
        if only and sid not in only:
            continue
        mp3, meta = vdir / f"{sid}.mp3", vdir / f"{sid}.json"
        h = hashlib.sha1(f"{text}|{voice_id}|{vcfg['model_id']}|{json.dumps(vcfg['settings'])}|{a.mock}".encode()).hexdigest()
        if mp3.exists() and meta.exists() and not a.force and read_json(meta).get("hash") == h:
            print(f"[cache] {sid}")
            continue

        print(f"[tts] {sid}: {text[:50]}...")
        if a.mock:
            align = mock_tts(text, mp3)
        else:
            body = {
                "text": text,
                "model_id": vcfg["model_id"],
                "voice_settings": vcfg["settings"],
                # continuity between scenes so intonation flows like one take
                "previous_text": items[idx - 1][1] if idx > 0 else None,
                "next_text": items[idx + 1][1] if idx + 1 < len(items) else None,
            }
            body = {k: v for k, v in body.items() if v is not None}
            r = requests.post(API.format(voice=voice_id), params={"output_format": "mp3_44100_128"},
                              json=body, headers={"xi-api-key": key}, timeout=180)
            if r.status_code >= 300:
                raise SystemExit(f"[x] ElevenLabs {r.status_code}: {r.text}")
            data = r.json()
            mp3.write_bytes(base64.b64decode(data["audio_base64"]))
            align = data.get("alignment") or data.get("normalized_alignment")

        write_json(meta, {"hash": h, "text": text, "duration": probe_duration(mp3), "alignment": align})
        print(f"   -> {mp3.name}")
    print("[ok] voice ready in", vdir)


if __name__ == "__main__":
    main()
