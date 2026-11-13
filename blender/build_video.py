"""Blender: build the episode in the Video Sequence Editor from timeline.json and render MP4.

Run with the Blender binary:
    blender -b --factory-startup --python-exit-code 1 -P blender/build_video.py -- build/ep02_communism/timeline.json
or with the bpy pip module (headless servers):
    python blender/build_video.py build/ep02_communism/timeline.json

Options (after the timeline path):
    --half            render at 50% resolution (fast preview)
    --stills 0,90,300 render only these frames as PNG (layout check), no video
    --save-blend      also save a .blend next to the video (open & tweak by hand in Blender)
"""
import json
import math
import os
import sys

import bpy

try:
    from bpy_extras import anim_utils
except ImportError:  # very old Blender
    anim_utils = None


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    opts = {"half": "--half" in argv, "save_blend": "--save-blend" in argv, "stills": None}
    if "--stills" in argv:
        opts["stills"] = [int(x) for x in argv[argv.index("--stills") + 1].split(",")]
    path = next(a for a in argv if a.endswith(".json"))
    return path, opts


def fcurves_of(scene):
    ad = scene.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if anim_utils and hasattr(anim_utils, "action_get_channelbag_for_slot"):
        bag = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        return list(bag.fcurves) if bag else []
    return list(act.fcurves)  # Blender < 4.4


def main():
    tl_path, opts = parse_args()
    with open(tl_path, encoding="utf-8") as f:
        tl = json.load(f)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    r = scene.render
    r.resolution_x, r.resolution_y = tl["width"], tl["height"]
    r.resolution_percentage = 50 if opts["half"] else 100
    r.fps, r.fps_base = tl["fps"], 1.0
    scene.frame_start, scene.frame_end = 1, tl["frame_end"]
    scene.view_settings.view_transform = "Standard"   # keep brand colors exact (no AgX/Filmic)
    scene.view_settings.look = "None"
    r.use_sequencer = True

    ed = scene.sequence_editor_create()
    strips = ed.strips

    bg = strips.new_effect("BG", type="COLOR", channel=1, frame_start=1, length=tl["frame_end"] + 1)
    bg.color = tl["bg"]

    interp = {}  # (data_path, index, frame) -> interpolation
    for im in tl["images"]:
        s = strips.new_image(im["name"], im["path"], im["channel"], im["start"] + 1, fit_method="ORIGINAL")
        s.frame_final_end = im["end"] + 1
        s.blend_type = "ALPHA_OVER"
        tr = s.transform

        targets = {
            "x": [(tr, "offset_x", None, 1.0)],
            "y": [(tr, "offset_y", None, 1.0)],
            "scale": [(tr, "scale_x", None, 1.0), (tr, "scale_y", None, 1.0)],
            "rot": [(tr, "rotation", None, math.pi / 180.0)],
            "alpha": [(s, "blend_alpha", None, 1.0)],
        }
        for prop, keys in im["keys"].items():
            for owner, attr, _, mul in targets[prop]:
                if not keys:
                    continue
                for frame, val, ip in keys:
                    setattr(owner, attr, val * mul)
                    owner.keyframe_insert(attr, frame=frame + 1)
                    interp[(owner.path_from_id(attr), frame + 1)] = ip

    for fc in fcurves_of(scene):
        for kp in fc.keyframe_points:
            ip = interp.get((fc.data_path, int(round(kp.co.x))), "BEZIER")
            kp.interpolation = ip
            if ip == "SINE":
                kp.easing = "EASE_IN_OUT"
        fc.update()

    for i, snd in enumerate(tl["sounds"]):
        s = strips.new_sound(f"snd{i}", snd["path"], snd["channel"], snd["start"] + 1)
        s.volume = snd["volume"]

    out = tl["out"]
    os.makedirs(os.path.dirname(out), exist_ok=True)

    if opts["stills"]:
        ims = r.image_settings
        ims.media_type = "IMAGE" if hasattr(ims, "media_type") else ims.media_type
        ims.file_format = "PNG"
        for fr in opts["stills"]:
            scene.frame_set(fr)
            r.filepath = out.replace(".mp4", f"_still_{fr:04d}.png")
            bpy.ops.render.render(write_still=True)
            print("[still]", r.filepath)
        return

    ims = r.image_settings
    if hasattr(ims, "media_type"):          # Blender 5.x
        ims.media_type = "VIDEO"
    ims.file_format = "FFMPEG"
    ff = r.ffmpeg
    ff.format, ff.codec = "MPEG4", "H264"
    ff.constant_rate_factor = "HIGH"
    ff.ffmpeg_preset = "GOOD"
    ff.gopsize = tl["fps"]
    ff.audio_codec, ff.audio_bitrate = "AAC", 192
    ff.audio_channels, ff.audio_mixrate = "STEREO", 48000
    r.filepath = out
    print(f"[render] {tl['frame_end']} frames -> {out}")
    bpy.ops.render.render(animation=True)

    if opts["save_blend"]:
        bpy.ops.wm.save_as_mainfile(filepath=out.replace(".mp4", ".blend"))
    print("[ok]", out)


if __name__ == "__main__":
    main()
