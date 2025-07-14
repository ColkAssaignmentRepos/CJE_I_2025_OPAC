#!/bin/sh

# Required commands:
#  curl, git

# Usage:
#   ./install.sh "python main.py"

# Constants
GIT_HTTPS_URL_TO_CLONE="https://github.com/ColkAssaignmentRepos/CJE_I_2025_OPAC_API.git"

# Check if 'uv' is installed; if not, install it
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# If `uv.lock` does not exist, clone the repository into the current directory
if [ ! -e "./uv.lock" ]; then
  git clone --recursive "$GIT_HTTPS_URL_TO_CLONE" .
fi

if [ ! -e "./cje1gw/" ]; then
  echo "[ERROR] './cje1gw' not found in the pwd. Please place the directory."
fi

# Set up the environment
uv venv && \
uv sync

echo "[INFO] Installed."

exit 0
