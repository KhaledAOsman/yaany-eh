#!/usr/bin/env bash
# حلقة كاملة بأمر واحد:
#   ./run_episode.sh episodes/02_communism.yaml              # إنتاج حقيقي
#   ./run_episode.sh episodes/02_communism.yaml --mock       # تجربة بدون APIs (مجانية)
#   ./run_episode.sh episodes/02_communism.yaml --half       # ريندر سريع نص الدقة
#   ./run_episode.sh episodes/02_communism.yaml --publish    # + رفع على GitHub Releases
#   ./run_episode.sh episodes/02_communism.yaml --stills     # صور للمراجعة بدل الفيديو
set -euo pipefail
cd "$(dirname "$0")"

EP="${1:?usage: ./run_episode.sh episodes/XX.yaml [--mock] [--half] [--publish] [--stills]}"; shift
MOCK=""; HALF=""; PUBLISH=0; STILLS=0
for a in "$@"; do
  case "$a" in
    --mock) MOCK="--mock" ;;
    --half) HALF="--half" ;;
    --publish) PUBLISH=1 ;;
    --stills) STILLS=1 ;;
  esac
done

# venv من setup.sh (لو موجود)
VENV="${VENV:-$HOME/yaany-venv}"
[ -f "$VENV/bin/activate" ] && source "$VENV/bin/activate"
PY="${PY:-python}"

echo "== 1/5 SFX library";   $PY tools/gen_sfx.py $MOCK
echo "== 2/5 Assets";        $PY tools/gen_assets.py "$EP" $MOCK
echo "== 3/5 Voice-over";    $PY tools/gen_voice.py "$EP" $MOCK
echo "== 4/5 Timeline";      $PY tools/plan_timeline.py "$EP"

ID=$($PY -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1],encoding='utf-8'))['id'])" "$EP")
TL="${YAANY_BUILD:-build}/$ID/timeline.json"
EXTRA="$HALF"
if [ "$STILLS" = 1 ]; then
  N=$($PY -c "import json,sys;print(json.load(open(sys.argv[1]))['frame_end'])" "$TL")
  EXTRA="--stills $(( N/10 )),$(( N*3/10 )),$(( N/2 )),$(( N*7/10 )),$(( N*9/10 ))"
fi

echo "== 5/5 Blender render"
if [ -n "${BLENDER:-}" ]; then
  "$BLENDER" -b --factory-startup --python-exit-code 1 -P blender/build_video.py -- "$TL" $EXTRA
else
  $PY blender/build_video.py "$TL" $EXTRA
fi

if [ "$PUBLISH" = 1 ] && [ "$STILLS" = 0 ]; then
  bash tools/publish.sh "$ID"
fi
echo "== done: ${YAANY_BUILD:-build}/$ID/"
