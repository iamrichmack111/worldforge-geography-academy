#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
REPO="${WORLDFORGE_REPO:-worldforge-geography-academy}"
PORT="${PORT:-8032}"
export PORT
command -v git >/dev/null || { echo 'Install git'; exit 1; }
command -v python3 >/dev/null || { echo 'Install Python 3'; exit 1; }
command -v ffmpeg >/dev/null || { echo 'Install ffmpeg'; exit 1; }
command -v gh >/dev/null || { echo 'Install GitHub CLI (gh) then gh auth login'; exit 1; }
gh auth status >/dev/null || { echo 'Run gh auth login first'; exit 1; }
if command -v docker >/dev/null && docker compose version >/dev/null 2>&1; then
  docker compose up --build -d
else
  echo 'Docker unavailable; using Python server for screenshots.'
  (PORT="$PORT" python3 server.py > /tmp/worldforge-release-server.log 2>&1 & echo $! > /tmp/worldforge-release.pid)
  trap 'if [ -f /tmp/worldforge-release.pid ]; then kill "$(cat /tmp/worldforge-release.pid)" 2>/dev/null || :; fi' EXIT
fi
python3 -m pip install --user playwright edge-tts >/dev/null 2>&1 || echo 'Python package installation skipped; ensure playwright is installed'
python3 -m playwright install chromium >/dev/null 2>&1 || echo 'Browser installation may require additional OS libraries'
export WORLDFORGE_DEMO_URL="http://127.0.0.1:$PORT"
for i in $(seq 1 45); do
  if python3 -c "import urllib.request; urllib.request.urlopen('$WORLDFORGE_DEMO_URL/classroom.html',timeout=2)" >/dev/null 2>&1; then break; fi
  sleep 1
done
python3 scripts/capture.py
python3 scripts/video.py
python3 -m unittest discover -s tests -p 'test_*.py' || { echo 'Some tests failed. Not publishing.'; exit 1; }
if [ ! -d .git ]; then git init -b main; fi
if [ ! -f README.md ]; then echo '# WorldForge' > README.md; fi
python3 scripts/readme.py
# Keep private data out of Git history.
git add -A ':!classroom.sqlite3' ':!media/tmp' ':!*.db' ':!*.env'
git commit -m 'Release WorldForge geography demo, Docker, screenshots and tests' || echo 'No changes to commit'
if ! gh repo view "$(gh api user -q .login)/$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --source=. --remote=origin --push
else
  URL="$(gh repo view "$(gh api user -q .login)/$REPO" --json url -q .url)"
  if ! git remote get-url origin >/dev/null 2>&1; then git remote add origin "${URL}.git"; fi
  git branch -M main
  git push -u origin main
fi
# GitHub releases support mp4 binaries and avoid Git LFS requirements.
TAG="demo-$(date +%Y%m%d-%H%M%S)"
gh release create "$TAG" media/demo.mp4 --title "WorldForge narrated demo" --notes 'Automated geography classroom walkthrough.' || echo 'GitHub release upload failed; local video is preserved.'
gh repo edit --description '3D geography classroom with homework, parent accounts, terrain quests, daily challenges and 100 dark themes.' \
 --add-topic geography --add-topic education --add-topic python --add-topic docker --add-topic playwright --add-topic homeschool --add-topic terrain-generation --add-topic edtech || true
printf '\nDone. Repo: https://github.com/%s/%s\nVideo: media/demo.mp4\nScreenshots: media/screenshots/\n' "$(gh api user -q .login)" "$REPO"
