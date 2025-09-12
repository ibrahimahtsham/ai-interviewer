#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/server"

usage() {
  cat <<EOF
AI Interviewer Frontend (code/) Run Help (non-interactive)

Frontend commands you can run manually:
  # Start Vite dev server
  npm run dev

  # Build (if build script exists)
  npm run build

  # Deploy (GitHub Pages or other) if configured
  npm run deploy

Recommended STT development workflow:
  1. In another terminal, read server/run.sh for backend instructions and start backend.
  2. Here run: npm run dev
  3. Open browser -> STT page.

Backend instructions have moved to: ../server/run.sh

This script only prints help; it performs no actions automatically.
EOF
}

usage
