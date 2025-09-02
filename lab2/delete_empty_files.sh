#!/bin/bash
(( $# == 1 )) || { echo "Usage: $0 <directory>" >&2; exit 1; }
dir="$1"
[[ -d "$dir" ]] || { echo "Error: '$dir' is not a directory." >&2; exit 1; }
find "$dir" -type f -empty -print -delete 2>/dev/null
