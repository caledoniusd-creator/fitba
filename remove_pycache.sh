#!/usr/bin/env bash
set -euo pipefail

echo "Removing __pycache__ directories..."

find . \
  -type d \
  -name "__pycache__" \
  -prune \
  -exec rm -rf {} +

echo "Done."
