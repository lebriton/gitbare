#!/bin/bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

# Install system dependencies
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    git-lfs \
    just \
    python3-pip \
    tmux

# Install git lfs
git lfs install

# Install pip packages
# NOTE: Install separately to avoid pip dependency resolution backtracking
pip install --break-system-packages pre-commit

# Configure project
just setup

# Install opencode
curl -fsSL https://opencode.ai/install | bash
