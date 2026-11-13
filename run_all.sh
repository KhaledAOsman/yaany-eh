#!/usr/bin/env bash
# ريندر كل حلقات السلسلة ورا بعض:
#   ./run_all.sh             # كل الحلقات + رفع
#   ./run_all.sh --stills    # صور مراجعة بس
set -euo pipefail
cd "$(dirname "$0")"
EXTRA="${*:---publish}"
for EP in episodes/*.yaml; do
  echo "################ $EP"
  bash ./run_episode.sh "$EP" $EXTRA
done
