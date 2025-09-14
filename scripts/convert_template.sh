#!/usr/bin/env bash
# Conversion script template for running FFmpeg commands listed in a file.
#
# Usage:
#   ./convert_template.sh -f commands.sh [-l convert.log] [-n]
#
# Options:
#   -f, --file FILE     Path to a file containing one FFmpeg command per line
#   -l, --log  FILE     Log file path (default: convert_YYYYMMDD_HHMMSS.log)
#   -n, --dry-run       Print commands without executing them
#
# Notes:
# - Lines beginning with '#' and blank lines are ignored.
# - Each command is executed independently; failures are logged and processing continues.
# - This script does not modify, reformat, or validate commands.

set -u -o pipefail

DRY_RUN=0
CMD_FILE=""
LOG_FILE=""

usage() {
  sed -n '1,25p' "$0" | sed 's/^# \{0,1\}//'
}

timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

default_log() {
  date "+convert_%Y%m%d_%H%M%S.log"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--file)
      CMD_FILE="${2:-}"
      shift 2
      ;;
    -l|--log)
      LOG_FILE="${2:-}"
      shift 2
      ;;
    -n|--dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$CMD_FILE" ]]; then
  echo "Error: --file is required" >&2
  usage
  exit 2
fi

if [[ ! -f "$CMD_FILE" ]]; then
  echo "Error: command file not found: $CMD_FILE" >&2
  exit 2
fi

if [[ -z "$LOG_FILE" ]]; then
  LOG_FILE="$(default_log)"
fi

echo "[INFO] $(timestamp) Starting conversion" | tee -a "$LOG_FILE"
echo "[INFO] Commands file: $CMD_FILE" | tee -a "$LOG_FILE"
echo "[INFO] Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "[INFO] Dry run: $DRY_RUN" | tee -a "$LOG_FILE"

TOTAL=0
SUCCESS=0
FAILED=0

while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip blanks and comments (with optional leading whitespace)
  if [[ "$line" =~ ^[[:space:]]*$ ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
    continue
  fi
  cmd="$line"

  TOTAL=$((TOTAL+1))
  echo "[RUN ] $(timestamp) $cmd" | tee -a "$LOG_FILE"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[SKIP] Dry run enabled" | tee -a "$LOG_FILE"
    continue
  fi

  # Execute the command and capture status
  bash -lc "$cmd" >>"$LOG_FILE" 2>&1
  rc=$?
  if [[ $rc -eq 0 ]]; then
    echo "[ OK ] $(timestamp) Completed" | tee -a "$LOG_FILE"
    SUCCESS=$((SUCCESS+1))
  else
    echo "[FAIL] $(timestamp) Exit code $rc" | tee -a "$LOG_FILE"
    FAILED=$((FAILED+1))
  fi
done < "$CMD_FILE"

echo "[INFO] $(timestamp) Done. total=$TOTAL ok=$SUCCESS failed=$FAILED" | tee -a "$LOG_FILE"

exit 0
