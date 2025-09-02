#!/bin/bash
start_hour="${START_HOUR:-9}"
end_hour="${END_HOUR:-18}"

today="$(date +%F)"
now_ts="$(date +%s)"
start_ts="$(date -d "$today $start_hour:00" +%s)"
end_ts="$(date -d "$today $end_hour:00" +%s)"

printf "Current time: %s\n" "$(date +'%Y-%m-%d %H:%M:%S %Z')"

if (( now_ts < start_ts )); then
  rem=$(( start_ts - now_ts ))
  printf "Work day hasn't started. Starts in %02d:%02d:%02d.\n" \
    $((rem/3600)) $(((rem%3600)/60)) $((rem%60))
elif (( now_ts >= end_ts )); then
  echo "Work day is over. Have a good rest!"
else
  rem=$(( end_ts - now_ts ))
  printf "Time remaining until end of work day: %02d:%02d:%02d.\n" \
    $((rem/3600)) $(((rem%3600)/60)) $((rem%60))
fi
