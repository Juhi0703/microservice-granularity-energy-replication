#!/bin/bash
# usage: cpu_log.sh out.csv   -- one row per container every ~5 s, until killed
# The timestamp uses the same clock format as Locust's logs, so trials can be matched.
echo "ts,container,cpu_pct,mem" > "$1"
while true; do
  ts=$(date '+%F %T')
  docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" | sed "s/^/$ts,/" >> "$1"
  sleep 3
done
