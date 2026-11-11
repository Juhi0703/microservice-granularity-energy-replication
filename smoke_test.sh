#!/bin/bash
# usage: bash ~/sde/smoke_test.sh pet_system/coarse
# Starts one configuration, waits, sends 2 minutes of the lowest load (40 req/s),
# then reports successes, failures per endpoint, stopped containers and memory.
# Containers stay up afterwards so you can read their logs.
set -u
source ~/sde-venv/bin/activate
EXP=~/sde/script_data/paper/experiment
cfg=$1; gran=$(basename "$cfg")
cd "$EXP/$cfg" || { echo "No such configuration: $cfg"; exit 1; }

docker compose up -d
echo "Waiting ${WARMUP:-300} s for the services to start and register..."
sleep "${WARMUP:-300}"
docker update --cpuset-cpus "${CONTAINER_CPUS:-2-11}" $(docker compose ps -q) > /dev/null
[[ $cfg == train_system/* ]] && bash ~/sde/fix_consign_id.sh

mkdir -p results "result05/$gran"; rm -f result05/"$gran"/*_0.log
echo "Sending load for 120 s..."
if [[ $cfg == pet_system/* ]]; then
  taskset -c 0,1 python ./locust_running.py -u 40 -r 40 --run-time 120s --iteration 0 > /dev/null 2>&1
else
  for n in 1 2 3 4; do
    taskset -c 0,1 python ./loadtesting/locust_$n.py -u 10 -r 40 --run-time 120s --iteration 0 > /dev/null 2>&1 &
  done
  wait
fi

ok=$(cat result05/"$gran"/*_0.log | grep -c 'SUCCESS:')
bad=$(cat result05/"$gran"/*_0.log | grep -c 'FAILURE:')
echo; echo "== $cfg: SUCCESS=$ok  FAILURE=$bad"
if [ "$bad" -gt 0 ]; then
  echo "Failures by endpoint (count, method, endpoint):"
  grep -h 'FAILURE:' result05/"$gran"/*_0.log | awk '{print $5, $6}' | sort | uniq -c | sort -rn | head -15
fi
echo; echo "Containers that are not running:"
docker compose ps -a --format '{{.Name}}  {{.Status}}' | grep -v ' Up ' || echo "  none"
echo; docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}'
echo; echo "Containers are still up. When done:  cd $EXP/$cfg && docker compose down"
