#!/usr/bin/env bash
# تجهيز السيرفر (Ubuntu/Debian) مرة واحدة:
#   bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== system packages"
sudo apt-get update -y
sudo apt-get install -y ffmpeg git curl libgl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6

echo "== GitHub CLI"
if ! command -v gh >/dev/null; then
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
  sudo apt-get update -y && sudo apt-get install -y gh
fi

echo "== uv + Python 3.13 venv (Blender 5.2 bpy module needs 3.13)"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
VENV="${VENV:-$HOME/yaany-venv}"
uv venv -p 3.13 "$VENV"
source "$VENV/bin/activate"
uv pip install -r requirements.txt
uv pip install -r requirements-blender.txt   # Blender as a Python module (headless)

echo "== .env"
[ -f .env ] || { cp .env.example .env; echo "   -> edit .env and put your API keys"; }
chmod +x run_episode.sh tools/publish.sh

echo "== smoke test (no APIs)"
./run_episode.sh episodes/02_communism.yaml --mock --half
echo
echo "[ok] Server ready. Next:"
echo "   1) nano .env                       (Recraft + ElevenLabs keys)"
echo "   2) put style refs in style/refs/   then: python tools/make_style.py"
echo "   3) ./run_episode.sh episodes/02_communism.yaml --publish"
