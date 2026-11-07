#!/usr/bin/env bash
# Check shell scripts with bash/sh syntax and shellcheck (when installed).
#
# Usage: ./check_script.sh <file> [file...]
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <file> [file...]" >&2
  exit 1
fi

status=0
for file in "$@"; do
  if [ ! -f "$file" ]; then
    echo "$file: no such file" >&2
    status=1
    continue
  fi

  shebang="$(head -n 1 "$file")"
  case "$shebang" in
    *'/sh'*)
      if ! sh -n "$file"; then
        status=1
      fi
      ;;
    *)
      if ! bash -n "$file"; then
        status=1
      fi
      ;;
  esac

  if command -v shellcheck >/dev/null 2>&1; then
    if ! shellcheck -x "$file"; then
      status=1
    fi
  else
    echo "note: shellcheck not installed; ran syntax check only for $file" >&2
  fi
done

exit "$status"
