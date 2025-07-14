#!/bin/sh

# Required commands:
#  curl, git

# Usage:
#   ./install.sh "python main.py"

# Constants
GIT_HTTPS_URL_TO_CLONE="https://github.com/ColkAssaignmentRepos/CJE_I_2025_OPAC_API.git"
INSTALL_CJE1_TOOLS_FILE_NAME="cje1install.sh"

# Check if 'uv' is installed; if not, install it
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# If `uv.lock` does not exist, clone the repository into the current directory
if [ ! -e "./uv.lock" ]; then
  git clone --recursive "$GIT_HTTPS_URL_TO_CLONE" .
fi

if [ ! -e "./$INSTALL_CJE1_TOOLS_FILE_NAME" ]; then
  echo "[ERROR] './$INSTALL_CJE1_TOOLS_FILE_NAME' not found in the pwd. Please download the file from manaba (student only) and place in the pwd."
fi

sh ./$INSTALL_CJE1_TOOLS_FILE_NAME

cp -R /tmp/pycode/cje1gw/ ./cje1gw

# Set up the environment
uv venv && \
uv sync

echo "[INFO] Installed."

exit 0
