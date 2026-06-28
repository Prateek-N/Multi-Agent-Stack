#!/usr/bin/env bash
# quickstart.sh — One-command setup for agents-maker
#
# Usage (from your project root, with agents-maker/ cloned inside it):
#   bash agents-maker/quickstart.sh
#   bash agents-maker/quickstart.sh --update     # regenerate system_prompt.md
#   bash agents-maker/quickstart.sh --skip-init  # skip init, just validate + show usage
#   bash agents-maker/quickstart.sh --no-color   # plain output (CI/logging)
#
# What it does:
#   1. Checks Python 3.9+ is available
#   2. Installs pyyaml (the only runtime dependency)
#   3. Runs tools/validate_kit.py to confirm the kit is intact
#   4. Runs tools/init_project.py to scan your project and generate system_prompt.md
#   5. Prints everything you need to run your first session

set -euo pipefail

# ---------------------------------------------------------------------------
# Arg parsing
# ---------------------------------------------------------------------------
UPDATE_FLAG=""
SKIP_INIT=0
NO_COLOR=0

for arg in "$@"; do
  case "$arg" in
    --update)     UPDATE_FLAG="--update" ;;
    --skip-init)  SKIP_INIT=1 ;;
    --no-color)   NO_COLOR=1 ;;
    --help|-h)
      # Print only the leading doc block (lines 2..first blank line)
      tail -n +2 "$0" | while IFS= read -r line; do
        [[ "$line" =~ ^# ]] || break
        echo "${line#\# }" | sed 's/^#$//'
      done
      exit 0
      ;;
    *)
      echo "Unknown option: $arg  (use --help for usage)" >&2
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
if [[ $NO_COLOR -eq 0 && -t 1 ]]; then
  GREEN="\033[0;32m"
  YELLOW="\033[0;33m"
  CYAN="\033[0;36m"
  RED="\033[0;31m"
  BOLD="\033[1m"
  RESET="\033[0m"
else
  GREEN="" YELLOW="" CYAN="" RED="" BOLD="" RESET=""
fi

ok()   { echo -e "${GREEN}[OK]${RESET}    $*"; }
info() { echo -e "${CYAN}[INFO]${RESET}  $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
fail() { echo -e "${RED}[FAIL]${RESET}  $*" >&2; }
step() { echo -e "\n${BOLD}==> $*${RESET}"; }
hr()   { echo -e "${CYAN}$(printf '%.0s─' {1..60})${RESET}"; }

# ---------------------------------------------------------------------------
# Locate kit directory (the directory this script lives in)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(dirname "$KIT_DIR")"

hr
echo -e "${BOLD}  agents-maker quickstart${RESET}"
echo "  Kit:     $KIT_DIR"
echo "  Project: $PROJECT_ROOT"
hr

# ---------------------------------------------------------------------------
# Step 1 — Python version check
# ---------------------------------------------------------------------------
step "Step 1 — Checking Python"

PY=""
for candidate in python3 python python3.12 python3.11 python3.10 python3.9; do
  if command -v "$candidate" &>/dev/null; then
    version=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    major="${version%%.*}"
    minor="${version#*.}"
    if [[ $major -ge 3 && $minor -ge 9 ]]; then
      PY="$candidate"
      ok "Found Python $version at $(command -v "$candidate")"
      break
    else
      warn "Skipping $candidate ($version) — need 3.9+"
    fi
  fi
done

if [[ -z "$PY" ]]; then
  fail "Python 3.9+ not found. Install from https://python.org and re-run."
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 2 — Install dependencies
# ---------------------------------------------------------------------------
step "Step 2 — Installing dependencies"

REQ="$KIT_DIR/requirements.txt"
if [[ ! -f "$REQ" ]]; then
  fail "requirements.txt not found at $REQ"
  exit 1
fi

if "$PY" -m pip install -r "$REQ" --quiet; then
  ok "Dependencies installed (pyyaml)"
else
  fail "pip install failed. Try: $PY -m pip install pyyaml"
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 3 — Validate kit integrity
# ---------------------------------------------------------------------------
step "Step 3 — Validating kit integrity"

VALIDATOR="$KIT_DIR/tools/validate_kit.py"
if [[ ! -f "$VALIDATOR" ]]; then
  fail "tools/validate_kit.py not found — is the kit complete?"
  exit 1
fi

if "$PY" "$VALIDATOR"; then
  ok "All integrity checks passed"
else
  fail "Kit validation failed — see output above."
  echo ""
  echo "  If you modified agent or skill files, re-run validate_kit.py manually:"
  echo "    $PY agents-maker/tools/validate_kit.py"
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 4 — init_project.py
# ---------------------------------------------------------------------------
if [[ $SKIP_INIT -eq 0 ]]; then
  step "Step 4 — Initializing project (generating system_prompt.md)"

  INIT="$KIT_DIR/tools/init_project.py"
  if [[ ! -f "$INIT" ]]; then
    fail "tools/init_project.py not found — is the kit complete?"
    exit 1
  fi

  echo ""
  info "Running: $PY $INIT $UPDATE_FLAG --path $PROJECT_ROOT"
  info "You will be asked to confirm or override the detected domain."
  echo ""

  # Run with --path so init_project.py scans the correct project root
  if "$PY" "$INIT" $UPDATE_FLAG --path "$PROJECT_ROOT"; then
    ok "init_project.py completed"
  else
    fail "init_project.py failed — see output above."
    exit 1
  fi
else
  step "Step 4 — Skipping init (--skip-init)"
  info "system_prompt.md was not regenerated."
fi

# ---------------------------------------------------------------------------
# Step 5 — Final summary and usage guide
# ---------------------------------------------------------------------------
SYSTEM_PROMPT="$KIT_DIR/system_prompt.md"

echo ""
hr
echo -e "${BOLD}  Setup complete. Here is everything you need to know.${RESET}"
hr
echo ""

# system_prompt.md status
if [[ -f "$SYSTEM_PROMPT" ]]; then
  CHARS=$(wc -c < "$SYSTEM_PROMPT" | tr -d ' ')
  TOKENS=$(( CHARS / 4 ))
  ok "system_prompt.md  (~${CHARS} chars, ~${TOKENS} tokens)"
  echo "  Paste it into your AI tool's system prompt / project instructions."
  echo "  You only need to do this once per AI context."
else
  warn "system_prompt.md was not created. Run init without --skip-init."
fi

echo ""
echo -e "${BOLD}  How to generate prompts${RESET}"
echo ""
echo "  Basic:"
echo "    $PY agents-maker/tools/generate_prompt.py \"describe your task here\""
echo ""
echo "  With phase:"
echo "    $PY agents-maker/tools/generate_prompt.py \"your task\" --phase implementation"
echo "    $PY agents-maker/tools/generate_prompt.py \"your task\" --phase review"
echo "    $PY agents-maker/tools/generate_prompt.py \"your task\" --phase solution_design"
echo ""
echo "  With token compression:"
echo "    $PY agents-maker/tools/generate_prompt.py \"your task\" --compress"
echo ""
echo "  With full system prompt (for models without persistent system prompt):"
echo "    $PY agents-maker/tools/generate_prompt.py \"your task\" --full"
echo ""
echo "  Valid phases: task_framing | requirements | solution_design |"
echo "                implementation | review_refinement | handoff"
echo ""
echo -e "${BOLD}  Context loaders (run these and paste the output with your task)${RESET}"
echo ""
echo "    $PY agents-maker/context_loaders/project_summary.py --path ."
echo "    $PY agents-maker/context_loaders/repo_tree.py --path ."
echo "    $PY agents-maker/context_loaders/file_chunker.py --path . --files src/main.py src/auth.py"
echo ""
echo -e "${BOLD}  Keeping system_prompt.md current${RESET}"
echo ""
echo "    bash agents-maker/quickstart.sh --update"
echo "    # or: $PY agents-maker/tools/init_project.py --update"
echo ""
echo -e "${BOLD}  Validate any time${RESET}"
echo ""
echo "    $PY agents-maker/tools/validate_kit.py"
echo ""
hr
echo ""
