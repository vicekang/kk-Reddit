#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[reddit-opencli] %s\n' "$*"
}

die() {
  printf '[reddit-opencli] ERROR: %s\n' "$*" >&2
  exit 1
}

if command -v opencli-rs >/dev/null 2>&1; then
  log "opencli-rs found: $(command -v opencli-rs)"
  opencli-rs --version || true
else
  command -v curl >/dev/null 2>&1 || die "curl is required to install opencli-rs"
  log "opencli-rs not found. Installing from upstream installer."
  curl -fsSL https://raw.githubusercontent.com/nashsu/opencli-rs/main/scripts/install.sh | sh
  command -v opencli-rs >/dev/null 2>&1 || die "opencli-rs is still missing after installer"
fi

log "Running diagnostics"
opencli-rs doctor || true

cat <<'EOF'

If diagnostics show "Chrome extension connected" as failed:
1. Install or enable the OpenCLI Chrome extension.
2. Open a Chrome window that is logged in to Reddit.
3. Run: opencli-rs doctor

EOF

