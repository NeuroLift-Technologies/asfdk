#!/usr/bin/env bash
# validate-governance.sh
# ORG-DEV-OTOI-1.0.2 · Governance Compliance Validation Script
# NeuroLift Technologies · .nltotoi/scripts/validate-governance.sh
#
# Usage: bash .nltotoi/scripts/validate-governance.sh [--strict] [--repo-root PATH]
#
# Exit codes:
#   0 — All required governance files present and valid
#   1 — One or more required files missing or invalid
#
# Options:
#   --strict    Treat warnings as errors (exit 1 on warnings)
#   --repo-root Specify repo root path (default: git repo root or current dir)

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────

SCRIPT_VERSION="1.0.0"
OTOI_VERSION="ORG-DEV-OTOI-1.0.2"

# Colors (only if stdout is a terminal)
if [ -t 1 ]; then
  RED='\033[0;31m'
  YELLOW='\033[1;33m'
  GREEN='\033[0;32m'
  BLUE='\033[0;34m'
  BOLD='\033[1m'
  RESET='\033[0m'
else
  RED='' YELLOW='' GREEN='' BLUE='' BOLD='' RESET=''
fi

# ─── Parse Arguments ──────────────────────────────────────────────────────────

STRICT=false
REPO_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict)
      STRICT=true
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: bash .nltotoi/scripts/validate-governance.sh [--strict] [--repo-root PATH]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Determine repo root
if [ -z "$REPO_ROOT" ]; then
  if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT="$(git rev-parse --show-toplevel)"
  else
    REPO_ROOT="$(pwd)"
  fi
fi

# ─── State Tracking ───────────────────────────────────────────────────────────

ERRORS=0
WARNINGS=0
CHECKS=0

# ─── Helper Functions ─────────────────────────────────────────────────────────

pass() {
  CHECKS=$((CHECKS + 1))
  echo -e "  ${GREEN}✓${RESET} $1"
}

fail() {
  CHECKS=$((CHECKS + 1))
  ERRORS=$((ERRORS + 1))
  echo -e "  ${RED}✗ ERROR:${RESET} $1"
}

warn() {
  CHECKS=$((CHECKS + 1))
  WARNINGS=$((WARNINGS + 1))
  echo -e "  ${YELLOW}⚠ WARN:${RESET}  $1"
  if [ "$STRICT" = true ]; then
    ERRORS=$((ERRORS + 1))
  fi
}

section() {
  echo ""
  echo -e "${BOLD}${BLUE}── $1 ──${RESET}"
}

check_file_exists() {
  local file="$REPO_ROOT/$1"
  local label="${2:-$1}"
  if [ -f "$file" ]; then
    pass "$label exists"
    return 0
  else
    fail "$label is MISSING ($1)"
    return 1
  fi
}

check_dir_exists() {
  local dir="$REPO_ROOT/$1"
  local label="${2:-$1}"
  if [ -d "$dir" ]; then
    pass "$label directory exists"
    return 0
  else
    fail "$label directory is MISSING ($1)"
    return 1
  fi
}

check_file_not_empty() {
  local file="$REPO_ROOT/$1"
  local label="${2:-$1}"
  if [ -f "$file" ] && [ -s "$file" ]; then
    pass "$label is non-empty"
    return 0
  elif [ -f "$file" ]; then
    warn "$label exists but is EMPTY ($1)"
    return 1
  fi
  # Missing file already caught by check_file_exists
  return 1
}

check_json_valid() {
  local file="$REPO_ROOT/$1"
  local label="${2:-$1}"
  if [ ! -f "$file" ]; then
    return 1  # Already reported as missing
  fi
  if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import json, sys; json.load(open('$file'))" 2>/dev/null; then
      pass "$label is valid JSON"
      return 0
    else
      fail "$label contains INVALID JSON ($1)"
      return 1
    fi
  elif command -v node >/dev/null 2>&1; then
    if node -e "JSON.parse(require('fs').readFileSync('$file','utf8'))" 2>/dev/null; then
      pass "$label is valid JSON"
      return 0
    else
      fail "$label contains INVALID JSON ($1)"
      return 1
    fi
  else
    warn "$label JSON validation skipped (python3 and node not available)"
    return 0
  fi
}

check_file_age() {
  local file="$REPO_ROOT/$1"
  local max_days="$2"
  local label="${3:-$1}"
  if [ ! -f "$file" ]; then
    return 1
  fi
  if command -v find >/dev/null 2>&1; then
    # Check if file was modified within max_days
    if find "$file" -mtime "-${max_days}" -print 2>/dev/null | grep -q .; then
      pass "$label updated within last ${max_days} days"
      return 0
    else
      warn "$label has NOT been updated in over ${max_days} days (may be stale)"
      return 1
    fi
  else
    warn "$label staleness check skipped (find not available)"
    return 0
  fi
}

# ─── Main Validation ──────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}NLT Governance Validation${RESET}"
echo -e "OTOI Version: ${OTOI_VERSION}"
echo -e "Script Version: ${SCRIPT_VERSION}"
echo -e "Repository: ${REPO_ROOT}"
echo -e "Strict Mode: ${STRICT}"

# ── Tier 1: Required OTOI Files ───────────────────────────────────────────────
section "Tier 1 — Required OTOI Files"

check_file_exists "CLAUDE.md"                          "CLAUDE.md (OTOI §4.1 Step 3)"
check_file_not_empty "CLAUDE.md"                       "CLAUDE.md"
check_file_exists "AGENTS.md"                          "AGENTS.md (OTOI §4.1 Step 2)"
check_file_not_empty "AGENTS.md"                       "AGENTS.md"
check_file_exists "docs/active-threads.md"             "docs/active-threads.md (OTOI §4.1 Step 4)"
check_file_not_empty "docs/active-threads.md"          "docs/active-threads.md"
check_file_exists "docs/agent-log/README.md"           "docs/agent-log/README.md"
check_dir_exists  "docs/agent-log/registrations"       "docs/agent-log/registrations"
check_file_exists "docs/agent-log/registrations/.gitkeep" "docs/agent-log/registrations/.gitkeep"
check_dir_exists  "docs/agent-log/handoffs"            "docs/agent-log/handoffs"
check_file_exists "docs/agent-log/handoffs/.gitkeep"   "docs/agent-log/handoffs/.gitkeep"

# ── Tier 2: Templates ─────────────────────────────────────────────────────────
section "Tier 2 — Governance Templates"

check_file_exists "templates/agent-registration.json"  "agent-registration.json template (OTOI §3)"
check_json_valid  "templates/agent-registration.json"  "agent-registration.json"
check_file_exists "templates/handoff-record.json"      "handoff-record.json template (OTOI §5)"
check_json_valid  "templates/handoff-record.json"      "handoff-record.json"
check_file_exists "templates/escalation.md"            "escalation.md template (OTOI §4.3)"
check_file_exists "templates/intent-log.md"            "intent-log.md template (OTOI §4.4)"

# ── Tier 3: SOPs ──────────────────────────────────────────────────────────────
section "Tier 3 — Standard Operating Procedures"

check_file_exists "SOPs/new-agent-onboarding.md"       "SOP-NLT-001: new-agent-onboarding.md"
check_file_exists "SOPs/repo-governance-setup.md"      "SOP-NLT-002: repo-governance-setup.md"
check_file_exists "SOPs/incident-response.md"          "SOP-NLT-003: incident-response.md"

# ── Tier 4: Issue Templates ───────────────────────────────────────────────────
section "Tier 4 — Issue Templates"

check_file_exists "ISSUE_TEMPLATE/agent-escalation.md"    "agent-escalation issue template"
check_file_exists "ISSUE_TEMPLATE/governance-proposal.md" "governance-proposal issue template"

# ── Tier 5: Governance Infrastructure ────────────────────────────────────────
section "Tier 5 — Governance Infrastructure"

check_file_exists ".nltotoi/index/governance-files.md"    ".nltotoi governance file registry"
check_file_exists ".nltotoi/scripts/validate-governance.sh" "validate-governance.sh (this script)"

# ── Staleness Checks ──────────────────────────────────────────────────────────
section "Staleness Checks"

check_file_age "docs/active-threads.md" 30 "docs/active-threads.md"

# ── Agent Log Checks (warnings only) ─────────────────────────────────────────
section "Agent Log Checks (informational)"

REG_DIR="$REPO_ROOT/docs/agent-log/registrations"
HANDOFF_DIR="$REPO_ROOT/docs/agent-log/handoffs"

REG_COUNT=$(find "$REG_DIR" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
HANDOFF_COUNT=$(find "$HANDOFF_DIR" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')

echo -e "  ${BLUE}ℹ${RESET}  Registrations on file: ${REG_COUNT}"
echo -e "  ${BLUE}ℹ${RESET}  Handoff records on file: ${HANDOFF_COUNT}"

if [ "$REG_COUNT" -gt 0 ] && [ "$HANDOFF_COUNT" -lt "$REG_COUNT" ]; then
  warn "More registrations (${REG_COUNT}) than handoff records (${HANDOFF_COUNT}) — possible orphaned sessions"
fi

# ─── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo "────────────────────────────────────────"
echo -e "${BOLD}Validation Summary${RESET}"
echo "────────────────────────────────────────"
echo -e "  Total checks:  ${CHECKS}"
echo -e "  ${GREEN}Passed:${RESET}        $((CHECKS - ERRORS - WARNINGS))"
echo -e "  ${YELLOW}Warnings:${RESET}      ${WARNINGS}"
echo -e "  ${RED}Errors:${RESET}        ${ERRORS}"
echo "────────────────────────────────────────"

if [ "$ERRORS" -gt 0 ]; then
  echo -e "${RED}${BOLD}RESULT: FAILED — ${ERRORS} error(s) found. Governance is NOT compliant.${RESET}"
  echo ""
  echo "To resolve, add the missing files or fix the listed issues."
  echo "Reference: SOPs/repo-governance-setup.md (SOP-NLT-002)"
  echo "Escalate to: joshua@neurolift.tech"
  echo ""
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  echo -e "${YELLOW}${BOLD}RESULT: PASSED WITH WARNINGS — ${WARNINGS} warning(s). Review recommended.${RESET}"
  echo ""
  exit 0
else
  echo -e "${GREEN}${BOLD}RESULT: PASSED — All governance files present and valid. ✓${RESET}"
  echo ""
  exit 0
fi
