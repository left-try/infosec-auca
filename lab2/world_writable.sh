#!/bin/bash
(( $# >= 1 )) || { echo "Usage: $0 <directory> [--no-sticky]" >&2; exit 1; }
dir="$1"; shift || true
[[ -d "$dir" ]] || { echo "Error: '$dir' is not a directory." >&2; exit 1; }

if [[ "${1:-}" == "--no-sticky" ]]; then
  find "$dir" -type d -perm -0002 ! -perm -1000 -print 2>/dev/null
else
  find "$dir" -type d -perm -0002 -print 2>/dev/null
fi
