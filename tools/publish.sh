#!/usr/bin/env bash
# رفع الفيديو على GitHub Releases (مش جوه الريبو نفسه — Git بيرفض الملفات > 100MB وبيتقل مع الفيديوهات)
#   bash tools/publish.sh ep02_communism
# محتاج: gh مسجّل دخول (gh auth login) أو GH_TOKEN في الـ environment
set -euo pipefail
cd "$(dirname "$0")/.."

ID="${1:?usage: tools/publish.sh <episode_id>}"
DIR="${YAANY_BUILD:-build}/$ID"
VIDEO="$DIR/$ID.mp4"
[ -f "$VIDEO" ] || { echo "[x] $VIDEO not found"; exit 1; }

TAG="$ID"
STAMP=$(date +%Y%m%d-%H%M)
cp "$VIDEO" "$DIR/${ID}_${STAMP}.mp4"   # نسخة بتاريخ عشان تحتفظ بكل الإصدارات

if ! gh release view "$TAG" >/dev/null 2>&1; then
  gh release create "$TAG" --title "يعني إيه — $ID" --notes "Rendered automatically by the pipeline."
fi
# الأحدث دايماً بنفس الاسم + نسخة مؤرخة
gh release upload "$TAG" "$VIDEO" "$DIR/${ID}_${STAMP}.mp4" "$DIR/timeline.json" --clobber
echo "[ok] uploaded -> $(gh release view "$TAG" --json url -q .url)"
