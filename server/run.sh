#!/usr/bin/env bash
set -euo pipefail

# Fresh Fedora FULL step-by-step guide (non-executing).
# This prints instructions only. Perform each STEP in order.

cat <<'EOF'
============================================================
 Local Speech-To-Text Server (Whisper tiny.en) - Fedora Guide
============================================================
Assumptions: Brand-new Fedora install, no Python 3.11, no build tools, repo cloned at: ~/Desktop/ai-interviewer
You are currently in: server/

LEGEND:
  (run)  = copy & paste the command in your terminal
  (check)= verify output / status

------------------------------------------------------------
STEP 0: Update system metadata (optional but recommended)
  (run)  sudo dnf update -y

------------------------------------------------------------
STEP 1: Install build tools & required development libraries
  (run)  sudo dnf install -y gcc gcc-c++ make \
            openssl-devel bzip2-devel libffi-devel zlib-devel xz-devel \
            readline-devel sqlite-devel tk-devel gdbm-devel uuid-devel \
            ncurses-devel
  (check) gcc --version  # should print a version (e.g. gcc (GCC) ...)

  (optional) If your Fedora variant still supports the group meta-package and you
             want the full group, you can ALSO try (will be skipped if unsupported):
    sudo dnf group install -y "Development Tools" || true
    sudo dnf group install --with-optional -y "Development Tools" || true

  (note) It's fine if those optional group commands say "No match"; the direct
         install above is enough for building Python 3.11 and wheels.

------------------------------------------------------------
STEP 2: Install pyenv (Python version manager)
  (run)  curl https://pyenv.run | bash

Add pyenv to your shell (TEMP for this session):
  (run)  export PATH="$HOME/.pyenv/bin:$PATH"
  (run)  eval "$(pyenv init -)"

To make pyenv permanent add these lines to ~/.bashrc (you can do later):
  export PATH="$HOME/.pyenv/bin:$PATH"
  eval "$(pyenv init -)"

------------------------------------------------------------
STEP 3: Install Python 3.11 with pyenv
  (run)  pyenv install 3.11.9
  (check) If it fails about compiler - ensure STEP 1 completed.

Set local version for this project (run in repo root):
  (run)  cd ~/Desktop/ai-interviewer
  (run)  pyenv local 3.11.9
  (check) python --version   # should show 3.11.9
  (run)  cd server

------------------------------------------------------------
STEP 4: Create isolated virtual environment (only once OR after deleting .venv)
  (run)  python -m venv .venv
  (check) ls .venv/bin/activate  # file should exist

------------------------------------------------------------
STEP 5: Activate virtual environment (every new terminal session)
  (run)  source .venv/bin/activate
  (check) prompt should now start with (venv) or (.venv)

If you see Python 3.13 inside venv accidentally:
  (run)  deactivate
  (run)  pyenv local 3.11.9   # (in repo root)
  (run)  rm -rf .venv && python -m venv .venv && source .venv/bin/activate

------------------------------------------------------------
STEP 6: Upgrade pip & install project dependencies
  (run)  pip install --upgrade pip
  (run)  pip install -r requirements.txt
  (check) python -c "import faster_whisper, websockets, numpy; print('Deps OK')"

If you STILL see build errors mentioning 'av' or ffmpeg with Python 3.11:
  (run)  pip install --upgrade 'faster-whisper>=1.0.0'

------------------------------------------------------------
STEP 7: Run the STT WebSocket server
  (ensure venv active)
  (run)  WHISPER_MODEL=tiny.en WHISPER_COMPUTE=int8 python stt_server.py
  (wait) First run downloads model; then expect line:
         [stt] ready ws://localhost:8765

Leave this terminal open while it runs.

------------------------------------------------------------
STEP 8: Start the frontend (in a NEW terminal window)
  (run)  cd ~/Desktop/ai-interviewer/code
  (run)  npm install   # first time only
  (run)  npm run dev
  (open) Browser -> URL shown (likely http://localhost:5173) -> go to STT page -> click Start.

------------------------------------------------------------
Stopping the server:
  In the server terminal: Ctrl + C

Deactivate venv:
  (run)  deactivate

------------------------------------------------------------
Reset everything (if things get messy):
  (run)  Ctrl + C  # stop server if running
  (run)  deactivate || true
  (run)  rm -rf .venv
  (run)  pyenv uninstall -f 3.11.9   # only if you truly want to re-install Python
  Then redo from STEP 1 (or STEP 2 if build tools already installed).

------------------------------------------------------------
Optional: Try a slightly better model (slower):
  (run)  WHISPER_MODEL=base WHISPER_COMPUTE=int8 python stt_server.py

Optional: Change port:
  (run)  STT_PORT=9000 WHISPER_MODEL=tiny.en WHISPER_COMPUTE=int8 python stt_server.py

------------------------------------------------------------
Quick one-liner (AFTER steps 1–3 done & if you want to recreate fast):
  rm -rf .venv && python -m venv .venv && source .venv/bin/activate && \
    pip install --upgrade pip && pip install -r requirements.txt && \
    WHISPER_MODEL=tiny.en WHISPER_COMPUTE=int8 python stt_server.py

Done. Follow steps in order; copy each (run) line into your terminal.
EOF
