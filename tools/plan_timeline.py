"""Turn episode YAML + voice timings into build/<ep>/timeline.json (frames, positions, keyframes).

Blender then just *executes* this file, so all the logic lives here and is testable without Blender.

    python tools/plan_timeline.py episodes/01_communism.yaml
"""
import argparse
import math
import re

from PIL import Image

from common import ROOT, SFX_DIR, color, ep_dir, episode, hex_rgb, read_json, series, write_json
from textcard import render_text

LEAD = 0.15     # silence before each scene's VO
TAIL = 0.45     # breathing room after VO
ANIM = 0.35     # default in/out animation length (s)
EXIT = 0.20     # fade-out of a scene's elements at the cut


class Planner:
    def __init__(self, cfg, ep, d):
        self.cfg, self.ep, self.d = cfg, ep, d
        self.fps = cfg["video"]["fps"]
        self.images, self.sounds = [], []
        self.sfx_k = 0
        self.warnings = []

    # ---------- time helpers ----------
    def f(self, sec):
        return int(round(sec * self.fps))

    def cue_time(self, sid, meta, cue):
        """seconds from VO start when `cue` word is spoken."""
        al = meta["alignment"]
        spoken = "".join(al["characters"])
        i = spoken.find(cue)
        if i < 0:
            self.warnings.append(f"cue '{cue}' not found in scene '{sid}' -> using 0.5s")
            return 0.5
        return al["character_start_times_seconds"][i]

    def when(self, sid, meta, vo_start, spec, default=0.0):
        if "cue" in spec:
            t = vo_start + self.cue_time(sid, meta, spec["cue"])
        else:  # "at" = seconds from the scene's start
            t = (vo_start - LEAD) + spec.get("at", default)
        return t + spec.get("delay", 0.0)

    # ---------- strips ----------
    def add_image(self, path, start, end, x, y, h=None, scale=None, channel=3, name=None):
        w0, h0 = Image.open(path).size
        s = scale if scale is not None else h / h0
        item = {
            "name": name or path.stem, "path": str(path), "channel": channel,
            "start": self.f(start), "end": max(self.f(end), self.f(start) + 1),
            "size": [w0, h0],
            "keys": {"x": [], "y": [], "scale": [], "alpha": [], "rot": []},
            "_rest": {"x": x, "y": y, "scale": s, "alpha": 1.0, "rot": 0.0},
        }
        self.images.append(item)
        return item

    def key(self, it, prop, t, v, interp="BEZIER"):
        it["keys"][prop].append([self.f(t), v, interp])

    def anim_in(self, it, t, kind):
        r = it["_rest"]
        t1 = t + ANIM
        self.key(it, "alpha", t, 0.0); self.key(it, "alpha", t + ANIM * 0.6, 1.0)
        if kind == "pop":
            self.key(it, "scale", t, r["scale"] * 0.2)
            self.key(it, "scale", t + ANIM * 0.7, r["scale"] * 1.12)
            self.key(it, "scale", t1, r["scale"])
        elif kind == "drop":
            self.key(it, "y", t, r["y"] + 520)
            self.key(it, "y", t + ANIM * 0.75, r["y"] - 24)
            self.key(it, "y", t1, r["y"])
        elif kind == "rise":
            self.key(it, "y", t, r["y"] - 260); self.key(it, "y", t1, r["y"])
        elif kind == "slide_left":
            self.key(it, "x", t, r["x"] - 900); self.key(it, "x", t1, r["x"])
        elif kind == "slide_right":
            self.key(it, "x", t, r["x"] + 900); self.key(it, "x", t1, r["x"])
        # "fade" = alpha only

    def anim_out(self, it, t, kind="fade", dur=EXIT):
        st = self.state_at(it, t)
        self.key(it, "alpha", t, st["alpha"]); self.key(it, "alpha", t + dur, 0.0)
        if kind == "drop_out":
            self.key(it, "y", t, st["y"]); self.key(it, "y", t + dur, st["y"] - 320)
        elif kind == "pop_out":
            self.key(it, "scale", t, st["scale"]); self.key(it, "scale", t + dur, 0.0)

    def state_at(self, it, t):
        """value of each prop at time t (last key <= t, else rest)."""
        fr = self.f(t)
        out = {}
        for p, ks in it["keys"].items():
            prev = [k for k in ks if k[0] <= fr]
            out[p] = max(prev, key=lambda k: k[0])[1] if prev else it["_rest"][p]
        return out

    def sound(self, path, t, volume, channel=None):
        if channel is None:
            channel = 71 + (self.sfx_k % 25)
            self.sfx_k += 1
        self.sounds.append({"path": str(path), "start": self.f(t), "channel": channel, "volume": volume})

    def sfx(self, name, t):
        p = SFX_DIR / f"{name}.mp3"
        if not p.exists():
            self.warnings.append(f"sfx '{name}' missing (run tools/gen_sfx.py)")
            return
        self.sound(p, t, self.cfg["audio"]["sfx_volume"])

    # ---------- text ----------
    def text_png(self, key, text, font, size, fill, **kw):
        out = self.d / "text" / f"{key}.png"
        render_text(text, out, font, size, fill, **kw)
        return out

    def captions(self, sid, meta, vo_start, end):
        cc = self.cfg["captions"]
        al = meta["alignment"]
        spoken = "".join(al["characters"])
        starts = al["character_start_times_seconds"]
        words = [(m.start(), m.group()) for m in re.finditer(r"\S+", spoken)]
        n = cc["words_per_chunk"]
        chunks = [words[i:i + n] for i in range(0, len(words), n)]
        for k, ch in enumerate(chunks):
            t0 = vo_start + starts[ch[0][0]]
            t1 = vo_start + starts[chunks[k + 1][0][0]] if k + 1 < len(chunks) else min(vo_start + meta["duration"] + 0.2, end)
            text = " ".join(w for _, w in ch).strip(" .،؛,:")
            if not text:
                continue
            png = self.text_png(f"cap_{sid}_{k}", text, self.cfg["fonts"]["bold"], cc["size"],
                                self.cfg["colors"]["white"], stroke=7,
                                stroke_fill=self.cfg["colors"]["caption_stroke"])
            it = self.add_image(png, t0, t1, 0, cc["y"], scale=1.0, channel=60, name=f"cap_{sid}_{k}")
            self.key(it, "scale", t0, 0.92); self.key(it, "scale", t0 + 0.12, 1.0)

    # ---------- scenes ----------
    def build(self):
        cfg, ep, d = self.cfg, self.ep, self.d
        t = 0.0
        scenes = list(ep["scenes"])
        if ep.get("teaser", {}).get("vo"):
            scenes.append({"id": "teaser", "type": "teaser", "vo": ep["teaser"]["vo"], "elements": [],
                           "sfx": [{"name": "whoosh", "at": 0.0}]})
        intro_end = None

        for sc in scenes:
            sid = sc["id"]
            meta = read_json(d / "voice" / f"{sid}.json")
            vo_start = t + LEAD
            dur = LEAD + meta["duration"] + TAIL
            if sc.get("type") == "intro":
                dur = max(dur, cfg["intro"]["duration"])
            if sc.get("type") == "teaser":
                dur += 0.8
            end = t + dur

            self.sound(d / "voice" / f"{sid}.mp3", vo_start, cfg["audio"]["vo_volume"], channel=70)
            for s in sc.get("sfx", []):
                self.sfx(s["name"], self.when(sid, meta, vo_start, s))

            if sc.get("type") == "intro":
                self.intro(sid, meta, t, vo_start, end)
                intro_end = end
            elif sc.get("type") == "teaser":
                self.teaser(sid, meta, t, vo_start, end)

            for i, el in enumerate(sc.get("elements", [])):
                self.element(sid, meta, vo_start, end, el, channel=3 + i)

            if cfg["captions"]["enabled"] and sc.get("type") not in ("intro", "teaser"):
                self.captions(sid, meta, vo_start, end)
            t = end

        total = t
        if cfg["badge"]["enabled"] and ep.get("badge"):
            self.badge(intro_end or 0.0, total)
        if cfg["audio"].get("music"):
            self.sound(ROOT / cfg["audio"]["music"], 0.0, cfg["audio"]["music_volume"], channel=99)
        return total

    def element(self, sid, meta, vo_start, end, el, channel):
        if "text" in el:  # Arabic text as an element
            el = dict(el, asset=el.get("id", f"txt{channel}"))
            path = self.text_png(f"el_{sid}_{channel}", el["text"], self.cfg["fonts"]["title"],
                                 el.get("size", 100), color(self.cfg, el.get("color", "white")))
            el.setdefault("h", Image.open(path).size[1])
        else:
            path = self.d / "assets" / f"{el['asset']}.png"
        if not path.exists():
            self.warnings.append(f"asset '{el['asset']}' missing (run tools/gen_assets.py)")
            return
        t_in = self.when(sid, meta, vo_start, el)
        it = self.add_image(path, t_in, end, el.get("x", 0), el.get("y", 0), h=el.get("h", 400),
                            channel=channel, name=f"{sid}_{el['asset']}_{channel}")
        r = it["_rest"]
        self.anim_in(it, t_in, el.get("in", "pop"))
        for prop in ("x", "y", "scale", "rot"):
            if not it["keys"][prop]:
                self.key(it, prop, t_in, r[prop])

        if el.get("spin"):
            self.key(it, "rot", t_in, 0.0, "LINEAR"); self.key(it, "rot", end, 50.0 * (end - t_in), "LINEAR")
        if el.get("float"):
            k, tt = 0, t_in + ANIM
            while tt < end:
                self.key(it, "y", tt, r["y"] + (14 if k % 2 else -14), "SINE"); tt += 0.9; k += 1
        if el.get("tilt"):
            tt = self.when(sid, meta, vo_start, el["tilt"])
            self.key(it, "rot", tt, 0.0); self.key(it, "rot", tt + 0.5, float(el["tilt"]["deg"]))

        for mv in el.get("moves", []):
            tm = self.when(sid, meta, vo_start, mv)
            st = self.state_at(it, tm)
            dur = mv.get("dur", 0.5)
            for p, v in (("x", mv.get("x")), ("y", mv.get("y"))):
                if v is not None:
                    self.key(it, p, tm, st[p]); self.key(it, p, tm + dur, v)
            if mv.get("h"):
                self.key(it, "scale", tm, st["scale"]); self.key(it, "scale", tm + dur, mv["h"] / it["size"][1])

        if el.get("out"):
            o = el["out"]
            to = self.when(sid, meta, vo_start, o)
            self.anim_out(it, to, o.get("anim", "fade"), o.get("dur", 0.3))
            it["end"] = self.f(to + o.get("dur", 0.3)) + 1
        else:
            self.anim_out(it, end - EXIT)

    def intro(self, sid, meta, t, vo_start, end):
        ic, c = self.cfg["intro"], self.cfg["colors"]
        kick = self.text_png("intro_kicker", ic["kicker_text"], self.cfg["fonts"]["title"], ic["kicker_size"], c["white"])
        it = self.add_image(kick, t, end, 0, ic["kicker_y"], scale=1.0, channel=62, name="intro_kicker")
        self.key(it, "alpha", t, 0.0); self.key(it, "alpha", t + 0.25, 1.0)
        self.anim_out(it, end - EXIT)

        word_col = color(self.cfg, self.ep.get("word_color", "gold"))
        word = self.text_png("intro_word", self.ep["word"], self.cfg["fonts"]["title"], ic["word_size"], word_col)
        tw = vo_start + self.cue_time(sid, meta, self.ep["word"])
        it = self.add_image(word, tw - 0.05, end, 0, 0, scale=1.0, channel=63, name="intro_word")
        self.anim_in(it, tw - 0.05, "drop")
        self.anim_out(it, end - EXIT, "pop_out")

    def teaser(self, sid, meta, t, vo_start, end):
        c, fnt = self.cfg["colors"], self.cfg["fonts"]
        lab = self.text_png("teaser_label", "الحلقة الجاية", fnt["bold"], 80, c["white"])
        it = self.add_image(lab, t + 0.1, end, 0, 330, scale=1.0, channel=62, name="teaser_label")
        self.anim_in(it, t + 0.1, "fade")
        kick = self.text_png("teaser_kicker", self.cfg["intro"]["kicker_text"], fnt["title"], 110, c["white"])
        it = self.add_image(kick, t + 0.3, end, 0, 150, scale=1.0, channel=63, name="teaser_kicker")
        self.anim_in(it, t + 0.3, "rise")
        nw = self.ep["teaser"]["word"]
        word = self.text_png("teaser_word", nw + "؟", fnt["title"], 170, c["gold"])
        tw = vo_start + self.cue_time(sid, meta, nw)
        it = self.add_image(word, tw, end, 0, -60, scale=1.0, channel=64, name="teaser_word")
        self.anim_in(it, tw, "drop")
        self.sfx("impact", tw)

    def badge(self, t0, t1):
        b, c = self.cfg["badge"], self.cfg["colors"]
        png = self.text_png("badge", self.ep["badge"], self.cfg["fonts"]["bold"], b["size"], c["bg"], pill=c["gold"])
        w, h = Image.open(png).size
        W, H = self.cfg["video"]["width"], self.cfg["video"]["height"]
        x = W / 2 - b["margin"] - w / 2          # top-right corner
        y = H / 2 - b["margin"] - 110 - h / 2    # below platform UI safe zone
        it = self.add_image(png, t0, t1, x, y, scale=1.0, channel=61, name="badge")
        self.anim_in(it, t0, "slide_right")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("episode")
    a = p.parse_args()
    cfg, ep = series(), episode(a.episode)
    d = ep_dir(ep)
    pl = Planner(cfg, ep, d)
    total = pl.build()

    for it in pl.images:
        rest = it.pop("_rest")
        for p_ in it["keys"]:
            if not it["keys"][p_]:   # static prop -> single constant key
                it["keys"][p_] = [[it["start"], rest[p_], "CONSTANT"]]
            it["keys"][p_].sort(key=lambda k: k[0])
    tl = {
        "width": cfg["video"]["width"], "height": cfg["video"]["height"], "fps": cfg["video"]["fps"],
        "bg": [v / 255 for v in hex_rgb(cfg["colors"]["bg"])],
        "frame_end": pl.f(total),
        "images": pl.images, "sounds": pl.sounds,
        "out": str(d / f"{ep['id']}.mp4"),
    }
    write_json(d / "timeline.json", tl)
    for w in pl.warnings:
        print("[!]", w)
    print(f"[ok] timeline: {total:.1f}s, {len(pl.images)} images, {len(pl.sounds)} sounds -> {d / 'timeline.json'}")


if __name__ == "__main__":
    main()
