#!/bin/bash
(( $# == 1 )) || { echo "Usage: $0 <directory>" >&2; exit 1; }
dir="$1"
[[ -d "$dir" ]] || { echo "Error: '$dir' is not a directory." >&2; exit 1; }
if [[ "${ONEFS:-0}" == "1" ]]; then
  find "$dir" -xdev \( -perm -4000 -o -perm -2000 \) -type f -exec ls -l {} \; 2>/dev/null
else
  find "$dir" \( -perm -4000 -o -perm -2000 \) -type f -exec ls -l {} \; 2>/dev/null
fi
