#!/usr/bin/env bash
set -euo pipefail
python -m unittest discover -s tests -v
if command -v terraform >/dev/null 2>&1; then
  terraform -chdir=infra fmt -check -recursive
  terraform -chdir=infra init -backend=false
  terraform -chdir=infra validate
else
  echo "Terraform not installed; skipped infrastructure validation." >&2
fi
