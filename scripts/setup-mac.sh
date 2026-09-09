#!/usr/bin/env bash
# One-time macOS setup. Safe to re-run.
set -e
if ! command -v brew >/dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
brew install git python@3.12 node
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install -r tools/requirements.txt
git init -q 2>/dev/null || true
echo "Done. Open this folder in VS Code and install the recommended extensions."
