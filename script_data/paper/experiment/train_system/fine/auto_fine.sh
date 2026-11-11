#!/bin/bash
# --- added for the WSL replication (see CHANGES.md) ---
cd "$(dirname "$0")"                 # always run from this folder
mkdir -p result05/fine              # Locust log folder (did not exist)
mkdir -p results                     # pre-create: the Locust files race to create it (FileExistsError)
LOCUST_CPUS=${LOCUST_CPUS:-0,1}      # Locust on cores 0-1; containers get 2-11
# ---------------------------------------------------------

iterations=${ITER:-10}
#duration between each iteration
delay=30

script_path_1="./loadtesting/locust_1.py"
script_path_2="./loadtesting/locust_2.py"
script_path_3="./loadtesting/locust_3.py"
script_path_4="./loadtesting/locust_4.py"

users_1=10
users_2=30
users_3=50
users_4=80
users_5=100

rate=40
runtime="120s"
pacing=1



printf "level_1 groups begins...\n"

for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_1, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path_1 -u $users_1 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_2 -u $users_1 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_3 -u $users_1 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_4 -u $users_1 -r $rate --run-time $runtime --iteration $i &
    sleep 120
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done
sleep 30

printf "level_2 groups begins...\n"
for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_2, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path_1 -u $users_2 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_2 -u $users_2 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_3 -u $users_2 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_4 -u $users_2 -r $rate --run-time $runtime --iteration $i &
    sleep 120
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done


printf "level_3 groups begins...\n"
for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_3, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path_1 -u $users_3 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_2 -u $users_3 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_3 -u $users_3 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_4 -u $users_3 -r $rate --run-time $runtime --iteration $i &
    sleep 120
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done

sleep 30
printf "level_4 groups begins...\n"
for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_4, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path_1 -u $users_4 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_2 -u $users_4 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_3 -u $users_4 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_4 -u $users_4 -r $rate --run-time $runtime --iteration $i &
    sleep 120
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done

sleep 30

printf "level_5 groups begins...\n"
for ((i=1; i<=iterations; i++))
do
    echo "Running iteration $i..."
    echo "Parameters: pacing=$pacing, users=$users_5, rate=$rate, runtime=$runtime, iteration=$i"
    taskset -c "$LOCUST_CPUS" python $script_path_1 -u $users_5 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_2 -u $users_5 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_3 -u $users_5 -r $rate --run-time $runtime --iteration $i &
    taskset -c "$LOCUST_CPUS" python $script_path_4 -u $users_5 -r $rate --run-time $runtime --iteration $i &
    sleep 120
    if [ $i -lt $iterations ]; then
        echo "Waiting for $delay seconds..."
        sleep $delay
    fi
done

echo "All iterations completed."