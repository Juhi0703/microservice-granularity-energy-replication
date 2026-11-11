#!/bin/bash
# --- added for the WSL replication (see CHANGES.md) ---
cd "$(dirname "$0")"                 # always run from this folder
mkdir -p result05/medium              # Locust log folder (did not exist)
mkdir -p results                     # pre-create: the Locust files race to create it (FileExistsError)
LOCUST_CPUS=${LOCUST_CPUS:-0,1}      # Locust on cores 0-1; containers get 2-11
# ---------------------------------------------------------

iterations=${ITER:-10}
#duration between each iteration
delay=30
script_path="./locust_running.py"

users_1=40
users_2=120
users_3=200
users_4=320
users_5=400

rate=40

runtime="120s"


printf "Burst high groups begins...\n"

for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_1, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path -u $users_1 -r $rate --run-time $runtime --iteration $i
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done

sleep 30
printf "Burst medium groups begins...\n"

for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_2, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path -u $users_2 -r $rate --run-time $runtime --iteration $i
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done

sleep 30
printf "Burst low groups begins...\n"

for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_3, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path -u $users_3 -r $rate --run-time $runtime --iteration $i
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done

sleep 30
printf "Even high groups begins...\n"

for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_4, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path -u $users_4 -r $rate --run-time $runtime --iteration $i
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done

sleep 30
printf "Even medium groups begins...\n"

for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_5, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path -u $users_5 -r $rate --run-time $runtime --iteration $i
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done

echo "All iterations completed."