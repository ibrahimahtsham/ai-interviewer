#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR/code"

if [[ "${1:-}" == "dev" ]]; then
  npm run dev
  exit $?
elif [[ "${1:-}" == "deploy" ]]; then
  npm run deploy
  exit $?
fi

echo "Select option:"
echo "  1) Start dev server (npm run dev)"
echo "  2) Deploy to GitHub Pages (build + publish)"
read -rp "Choice [1-2]: " choice

case "$choice" in
  1) npm run dev ;;
  2) npm run deploy ;;
  *) echo "Invalid choice" >&2; exit 1 ;;
esac
