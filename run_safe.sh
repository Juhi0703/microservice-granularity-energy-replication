#!/usr/bin/env bash
# One configuration at a time, 120 s pause before each,
# stop a configuration at once if a container fails to start,
# and flag runs that end too early or had refused connections.
EXP=~/sde/script_data/paper/experiment
for c in "$@"; do
  out=~/sde/out_${c//\//_}.txt
  echo "=== $(date '+%F %T') waiting 120 s before $c"
  sleep 120
  t0=$(date +%s)
  bash ~/sde/run_all.sh "$c" > "$out" 2>&1 &
  RUN=$!
  failed=0
  for i in $(seq 60); do
    sleep 10
    if grep -q "failed to start" "$out"; then failed=1; break; fi
    kill -0 $RUN 2>/dev/null || break
  done
  if [ $failed = 1 ]; then
    echo "!!! $(date '+%F %T') $c: a container failed to start, stopping it"
    pkill -f run_all.sh; pkill -f cpu_log.sh; pkill -f auto_; pkill -f locust
    sleep 5; (cd "$EXP/$c" && docker compose down)
    echo "$(date '+%F %T') FAILED $c" >> ~/sde/run_times.log
    continue
  fi
  echo "=== $(date '+%F %T') $c: containers OK, load test running (~130 min)"
  wait $RUN
  mins=$(( ($(date +%s) - t0) / 60 ))
  refused=$(grep -c "ConnectionRefused" "$out")
  echo "=== $(date '+%F %T') $c finished after $mins min, ConnectionRefused lines: $refused"
  if [ $mins -lt 100 ] || [ $refused -gt 0 ]; then
    echo "!!! $c looks wrong (expected ~130 min and 0 refused)"
    echo "$(date '+%F %T') CHECK $c ($mins min, $refused refused)" >> ~/sde/run_times.log
  fi
done
echo "=== ALL DONE $(date '+%F %T')"
