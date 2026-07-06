#!/bin/bash
# Enforce the repo's code-size limits:
#   python files <= 200 lines, js/jsx files <= 100 lines
set -e
cd "$(dirname "$0")/.."
fail=0

while read -r file; do
  lines=$(wc -l < "$file")
  if [ "$lines" -gt 200 ]; then
    echo "PYTHON FILE TOO LONG ($lines > 200): $file"
    fail=1
  fi
done < <(find services -name '*.py' -not -path '*/node_modules/*')

while read -r file; do
  lines=$(wc -l < "$file")
  if [ "$lines" -gt 100 ]; then
    echo "JS FILE TOO LONG ($lines > 100): $file"
    fail=1
  fi
done < <(find web/src -name '*.js' -o -name '*.jsx')

if [ "$fail" -eq 0 ]; then
  echo "file sizes OK"
fi
exit $fail
