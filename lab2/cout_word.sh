#!/bin/bash
insensitive=0
if [[ "${1:-}" == "-i" ]]; then insensitive=1; shift; fi
if (( $# != 2 )); then echo "Usage: $0 [-i] <file> <word>" >&2; exit 1; fi

file="$1"; word="$2"
[[ -f "$file" ]] || { echo "Error: '$file' is not a file." >&2; exit 1; }

if (( insensitive )); then
  count="$(grep -oiw -- "$word" "$file" | wc -l)"
else
  count="$(grep -ow -- "$word" "$file" | wc -l)"
fi
echo "$count"
