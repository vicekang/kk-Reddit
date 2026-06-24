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
  log "opencli is not installed. Install it with: npm install -g @jackwener/opencli"
fi

if command -v opencli-rs >/dev/null 2>&1; then
  log "opencli-rs found: $(command -v opencli-rs)"
  opencli-rs --version || true
else
  log "opencli-rs is not installed. Use KK_REDDIT_BACKEND=opencli to run through OpenCLI."
  log "Do not use the old nashsu/opencli-rs installer; that path now installs autocli."
fi

log "Running diagnostics"
if command -v opencli >/dev/null 2>&1; then
  opencli doctor || true
elif command -v opencli-rs >/dev/null 2>&1; then
  opencli-rs doctor || true
else
  die "Neither opencli nor opencli-rs is installed"
fi

cat <<'EOF'

If diagnostics show "Chrome extension connected" as failed:
1. Install or enable the OpenCLI Chrome extension.
2. Open a Chrome window that is logged in to Reddit.
3. Run: opencli doctor

Backend selection:
- Default wrapper backend: opencli-rs when present, otherwise opencli.
- Force OpenCLI: KK_REDDIT_BACKEND=opencli python3 redditctl.py check
- Force opencli-rs: KK_REDDIT_BACKEND=opencli-rs python3 redditctl.py check

EOF
