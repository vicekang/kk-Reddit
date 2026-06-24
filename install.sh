#!/usr/bin/env bash
set -euo pipefail

REPO_OWNER="${KK_REDDIT_OWNER:-vicekang}"
REPO_NAME="${KK_REDDIT_REPO:-kk-Reddit}"
REPO_BRANCH="${KK_REDDIT_BRANCH:-main}"
SKILL_NAME="reddit-opencli"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"

log() {
  printf '[kk-Reddit] %s\n' "$*" >&2
}

die() {
  printf '[kk-Reddit] ERROR: %s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

script_dir() {
  local src="${BASH_SOURCE[0]:-$0}"
  cd -- "$(dirname -- "$src")" >/dev/null 2>&1 && pwd
}

download_repo() {
  need_cmd curl
  need_cmd tar

  local tmp
  tmp="$(mktemp -d)"
  local archive="$tmp/${REPO_NAME}.tar.gz"
  local url="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/${REPO_BRANCH}.tar.gz"

  log "Downloading ${url}"
  curl -fsSL "$url" -o "$archive"
  tar -xzf "$archive" -C "$tmp"

  local root
  root="$(find "$tmp" -maxdepth 1 -type d -name "${REPO_NAME}-*" | head -n 1)"
  [ -n "$root" ] || die "Could not find extracted repository root"
  printf '%s\n' "$root"
}

resolve_repo_root() {
  local dir
  dir="$(script_dir || true)"

  if [ -n "${dir:-}" ] && [ -f "$dir/${SKILL_NAME}/SKILL.md" ]; then
    printf '%s\n' "$dir"
    return
  fi

  if [ -f "./${SKILL_NAME}/SKILL.md" ]; then
    pwd
    return
  fi

  download_repo
}

install_opencli_bridge() {
  if command -v opencli >/dev/null 2>&1; then
    log "opencli found: $(command -v opencli)"
    opencli --version || true
    return
  fi

  if ! command -v npm >/dev/null 2>&1; then
    log "opencli is missing and npm is not available; skipping automatic opencli install"
    return
  fi

  log "opencli not found. Installing @jackwener/opencli with npm."
  if npm install -g @jackwener/opencli; then
    log "opencli installed: $(command -v opencli)"
  else
    log "opencli install failed; install @jackwener/opencli manually if browser bridge setup is needed"
  fi
}

check_opencli_rs() {
  if command -v opencli-rs >/dev/null 2>&1; then
    log "opencli-rs found: $(command -v opencli-rs)"
    opencli-rs --version || true
    return
  fi

  log "opencli-rs is not installed. The wrapper can use opencli with KK_REDDIT_BACKEND=opencli."
  log "Not running the old opencli-rs installer because that upstream path now installs autocli."
}

main() {
  local repo_root
  repo_root="$(resolve_repo_root)"
  [ -f "$repo_root/${SKILL_NAME}/SKILL.md" ] || die "Missing ${SKILL_NAME}/SKILL.md in ${repo_root}"

  install_opencli_bridge
  check_opencli_rs

  mkdir -p "$DEST_ROOT"
  rm -rf "$DEST_ROOT/$SKILL_NAME"
  cp -R "$repo_root/$SKILL_NAME" "$DEST_ROOT/$SKILL_NAME"
  log "Installed Codex skill to $DEST_ROOT/$SKILL_NAME"

  if command -v opencli >/dev/null 2>&1; then
    log "Running opencli doctor"
    opencli doctor || true
  elif command -v opencli-rs >/dev/null 2>&1; then
    log "Running opencli-rs doctor"
    opencli-rs doctor || true
  fi

  cat <<'EOF'

Next steps:
1. Restart or refresh Codex so it discovers the reddit-opencli skill.
2. Run: opencli doctor
3. Optional: run opencli-rs doctor if you use the opencli-rs backend.
4. If "Chrome extension connected" is not checked, install/enable the OpenCLI Chrome extension.
   See docs/CHROME_EXTENSION.md in this repository for the exact flow.

EOF
}

main "$@"
