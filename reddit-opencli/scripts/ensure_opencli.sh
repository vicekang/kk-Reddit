#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[reddit-opencli] %s\n' "$*"
}

die() {
  printf '[reddit-opencli] ERROR: %s\n' "$*" >&2
  exit 1
}

if command -v opencli >/dev/null 2>&1; then
  log "opencli found: $(command -v opencli)"
  opencli --version || true
else
  command -v npm >/dev/null 2>&1 || die "opencli is missing and npm is not available"
  log "opencli not found. Installing @jackwener/opencli with npm."
  npm install -g @jackwener/opencli
  command -v opencli >/dev/null 2>&1 || die "opencli is still missing after npm install"
fi

log "Running diagnostics"
opencli doctor || true

cat <<'EOF'

If diagnostics show the Chrome extension is missing or unstable:
1. Install/update OpenCLI: npm install -g @jackwener/opencli
2. Open chrome://extensions and enable the OpenCLI extension.
3. Open a Chrome window that is logged in to Reddit.
4. Run: opencli doctor

EOF
