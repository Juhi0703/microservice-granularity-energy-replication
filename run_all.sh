#!/bin/bash
# usage: bash ~/sde/run_all.sh pet_system/coarse pet_system/medium pet_system/fine
#        bash ~/sde/run_all.sh train_system/coarse train_system/medium
# dry run (1 trial per level, ~17 min):  ITER=1 bash ~/sde/run_all.sh pet_system/coarse
#
# For each configuration: start containers, wait for registration, pin them to cores 2-11,
# log CPU, run the load script, shut down. Earlier logs are moved to old_runs/ first,
# so a dry run can never mix with a real run.
set -u
source ~/sde-venv/bin/activate
EXP=~/sde/script_data/paper/experiment
CONTAINER_CPUS=${CONTAINER_CPUS:-2-11}   # 12 logical processors; Locust uses 0-1
WARMUP=${WARMUP:-300}                    # seconds to wait after "docker compose up"

for cfg in "$@"; do
  cd "$EXP/$cfg" || { echo "No such configuration: $cfg"; exit 1; }
  if compgen -G "result05/*/*.log" > /dev/null || compgen -G "cpu_*.csv" > /dev/null; then
    old="old_runs/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$old"
    [ -d result05 ] && mv result05 "$old/"
    for f in cpu_*.csv; do [ -e "$f" ] && mv "$f" "$old/"; done
    echo "Moved earlier logs of $cfg to $cfg/$old"
  fi
  echo "$(date '+%F %T') start $cfg" | tee -a ~/sde/run_times.log
  docker compose up -d
  echo "Waiting $WARMUP s for the services to register..."
  sleep "$WARMUP"
  docker update --cpuset-cpus "$CONTAINER_CPUS" $(docker compose ps -q) > /dev/null
  [[ $cfg == train_system/* ]] && bash ~/sde/fix_consign_id.sh
  bash ~/sde/cpu_log.sh "cpu_$(echo "$cfg" | tr / _).csv" & LOGGER=$!
  bash ./auto_*.sh
  sleep 30                               # let the last 120 s trial finish
  kill $LOGGER
  echo "$(date '+%F %T') end $cfg" | tee -a ~/sde/run_times.log
  docker compose down
done
