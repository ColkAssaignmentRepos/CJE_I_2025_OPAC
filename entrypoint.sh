#!/bin/sh

# Required commands:
#  curl, git

# Usage:
#   ./entrypoint.sh "python main.py"

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

# Set up the environment
uv venv && \
uv sync

# Execute the given command using uv run
if [ $# -eq 0 ]; then
  echo "Usage: $0 <command to run via uv run>"
  exit 1
fi

uv run -- "$@"
