# يعني إيه — Pipeline إنتاج الحلقات

```
episodes/XX.yaml  ─┬─> Recraft (استوكات بنفس الاستايل)      -> build/<id>/assets/*.png
                   ├─> ElevenLabs TTS + توقيت كل حرف          -> build/<id>/voice/*.mp3/json
                   ├─> ElevenLabs Sound Effects (مرة واحدة)   -> sfx/*.mp3
                   ├─> نصوص عربي PNG (Tajawal)                -> build/<id>/text/*.png
                   └─> plan_timeline.py -> timeline.json -> Blender (VSE) -> <id>.mp4 -> GitHub Releases
```

## 1) تجهيز السيرفر (مرة واحدة)
```bash
git clone https://github.com/<you>/<repo>.git && cd <repo>
bash setup.sh            # ffmpeg + gh + Python 3.13 + Blender(bpy) + تجربة mock
nano .env                # RECRAFT_API_TOKEN / ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID
gh auth login            # عشان الرفع على Releases
```

## 2) تثبيت الاستايل (مرة واحدة للسلسلة كلها)
حط من 1 لـ 10 صور مرجعية في `style/refs/` (مرخصة/مشتراة، من غير علامة مائية) وبعدين:
```bash
python tools/make_style.py          # => style/style.json  (اعمله commit)
```

## 3) حلقة جديدة
1. انسخ `episodes/02_communism.yaml` وعدّل: `id`, `word`, `badge`, `teaser`, `assets`, `scenes`.
2. شغّل:
```bash
./run_episode.sh episodes/03_xxx.yaml --stills     # صور مراجعة سريعة
./run_episode.sh episodes/03_xxx.yaml --publish    # فيديو نهائي + رفع
```
أو بس اعمل `git push` للملف — الـ workflow هيعمل الريندر ويرفع لوحده (شوف تحت).

### تعديلات شائعة
| عايز | الأمر |
|---|---|
| تعيد توليد استوك واحد | `python tools/gen_assets.py EP.yaml --only coins --force` |
| 3 اختيارات لاستوك | `python tools/gen_assets.py EP.yaml --only owner --variants 3` ← اختار وسمّيه `owner.png` |
| تعيد صوت مشهد | `python tools/gen_voice.py EP.yaml --only story --force` |
| تفتح المشروع في Blender وتعدل بإيدك | `python blender/build_video.py build/<id>/timeline.json --save-blend` |

## 4) الحفظ على GitHub
الفيديوهات بتترفع على **Releases** (tag لكل حلقة) — مش جوه الريبو، عشان Git بيرفض أي ملف أكبر من 100MB والريبو بيتقل.
كل رفع بيحط `ep02_communism.mp4` (الأحدث) + نسخة بالتاريخ + `timeline.json`.

## 5) ريندر تلقائي مع كل push (Self-hosted runner)
1. GitHub → Settings → Actions → Runners → **New self-hosted runner** → Linux، ونفّذ الأوامر اللي بتظهر على السيرفر، وبعدين:
   ```bash
   sudo ./svc.sh install && sudo ./svc.sh start
   ```
2. Settings → Secrets and variables → Actions → أضف:
   `RECRAFT_API_TOKEN`, `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`
3. خلاص: أي ملف جديد/متعدل في `episodes/` => ريندر + Release. أو يدوي من Actions → render-episode → Run workflow.

## مرجع ملف الحلقة
- `cue: "كلمة"` العنصر يظهر لحظة نطق الكلمة (من توقيتات ElevenLabs) — `at: 1.5` بديل بالثواني.
- `in:` pop | drop | rise | slide_left | slide_right | fade
- `out: {anim: fade|drop_out|pop_out, cue: ...}` ، `moves: [{cue, x, y, h, dur}]`
- `spin: true` ، `float: true` ، `tilt: {cue, deg}` ، `delay: 0.12`
- الإحداثيات من منتصف الشاشة (1080×1920): x من -540 لـ 540 ، y من -960 لـ 960.
