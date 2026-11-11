# Changes to the authors' experiment scripts

These are the only changes made to the authors' files. `CHANGES.diff` is the line-by-line diff of the **first round** of changes (the first two sections below). The later changes are described in the sections "Added after the Train Ticket smoke test" and "Added during the real runs".
Use this list in the Method / Threats to validity part of your report.

## Needed to run on one laptop

| Files | Change | Why |
| --- | --- | --- |
| All 15 Locust files | `145.108.225.14` (the authors' server) → `localhost` | Services run on your laptop |
| 12 Train Ticket Locust files | Requests written as full URLs (`http://localhost:PORT/...`); `host = "http:"` → `"http://localhost"` | The original relied on gluing `"http:"` onto `"//IP:PORT"`; full URLs work with any Locust version |
| All 6 `auto_*.sh` | `../<granularity>_script/...` → `./...` | Those folders don't exist in the replication package |
| All 6 `auto_*.sh` | Added: `cd` to own folder, `mkdir -p result05/<granularity>` | Locust's log folder didn't exist, so the first run would fail |
| All 6 `auto_*.sh` | Removed the "level_0" idle phase | It was a 25-minute energy baseline for PowerStat, which this replication doesn't use |
| All 6 `auto_*.sh` | `python ...` → `taskset -c "$LOCUST_CPUS" python ...` (cores 0-1) | Load generator and services share one machine; pinning reduces interference |
| All 6 `auto_*.sh` | `iterations=10` → `iterations=${ITER:-10}` | Allows a short dry run with `ITER=1`; default is unchanged |

## Bugs fixed (these change behaviour compared with the authors' run)

| File | Bug | Effect in the authors' run |
| --- | --- | --- |
| `train_system/medium/loadtesting/locust_3.py` and `train_system/fine/loadtesting/locust_3.py` | `executeservice/welcome` URL was missing `//`, so the request URL was invalid | Every such request (1 of 40 operations) failed inside Locust without reaching the server, so medium and fine got slightly less real load than coarse |
| `train_system/fine/docker-compose.yml` | `- RABBITMQ_HOST` under `ts-preserve-other-service` was indented one space too far | YAML glued it onto the Eureka URL, giving a broken discovery address and no RabbitMQ host |

## Left exactly as the authors had them

- Load levels (40-400 req/s), `constant_pacing(1)`, 120 s trials, 30 s gaps, spawn rate 40, endpoints and request bodies.
- Pet Clinic coarse starts Locust in the background then sleeps 120 s; Pet Clinic medium and fine run it in the foreground. Same trial length either way.
- `ASSURANCE_MYQL_USER` (typo for MYSQL) in the Train Ticket compose files.
- Train Ticket fine has no 30 s pause between load levels 2 and 3.
- `version: '3'` in the Pet Clinic compose files (newer Docker prints a harmless "obsolete" warning).
- All four Train Ticket Locust processes write `--csv=locust_report` to the same file; those CSVs are not used in the analysis.

## Added files

`run_all.sh`, `smoke_test.sh`, `cpu_log.sh`, `analysis/*.py`. Containers are pinned to cores 2-11 by `run_all.sh` with `docker update --cpuset-cpus`; the compose files themselves are unchanged apart from the YAML fix above.

## Checks run on this package

- All 6 compose files parse as YAML; no environment entry contains a glued second entry.
- Every port that each granularity's Locust files call is published by that granularity's compose file (Pet Clinic 1 port; Train Ticket 10, 20 and 40 ports).
- All Python files compile; all shell scripts pass `bash -n`.
- The fixed Pet Clinic and Train Ticket coarse load scripts were run end to end (shortened timings) against local test servers with Locust 2.47; the logs were then processed by `process_logs.py`, `stats.py` and `plots.py` without errors.
- `reproduce_rq1.py` reproduces the paper's Table V exactly and Table VI's Cliff's delta values.

## Added after the Train Ticket smoke test

| File | Change | Why |
| --- | --- | --- |
| `fix_consign_id.sh` (new), called by `run_all.sh` and `smoke_test.sh` for Train Ticket | After the services start, reads the consign-price config id from MySQL and writes it into `loadtesting/locust_3.py` | Train Ticket creates that config with a new random id at every start. The authors' fixed id made every `POST /consignpriceservice/consignprice` fail with HTTP 500 (Hibernate: "identifier ... was altered"). The authors' own README (DEBUG) says to change the id of task23; this does it automatically |
| All 6 `auto_*.sh` and `smoke_test.sh` | `mkdir -p results` before starting Locust | Every Locust file runs `if not os.path.exists('results'): os.makedirs('results')` at import. When 4 Train Ticket processes start at the same moment in a folder without `results/`, one can crash with `FileExistsError` and send no requests at all. Seen in the Train Ticket medium smoke test (only 3 of 4 processes started) and reproduced on a test machine |
| `analysis/process_logs.py` | New columns `n_requests` and `n_processes`; prints a WARNING for any trial where fewer Locust processes started than expected (4 for Train Ticket, 1 for Pet Clinic) | So a crashed load generator can never hide inside the results |

## Added during the real runs

| File | Change | Why |
| --- | --- | --- |
| `pet_system/{coarse,medium}/docker-compose.override.yml` (new) | The config server uses the `native` profile and reads a local clone of `github.com/spring-petclinic/spring-petclinic-microservices-config` (commit `323993c`) mounted at `/config-repo` | The authors' setup clones the configuration from GitHub at every start. Offline (Wi-Fi off during measurements) the discovery server exited with code 1, and the health check (`curl -I`) did not notice. The authors' `docker-compose.yml` is unchanged |
| `pet_system/fine/docker-compose.override.yml` (new) | Same, but with a local clone of the authors' own config repository `github.com/Yimingzha0/spring-petclinic-fine-config` (commit `18dd339`) | The fine version needs the authors' `pets-service.yml`; with the upstream configuration every `/api/pet/petApi/...` request failed with HTTP 503 |
| `run_safe.sh` (new) | Wrapper around `run_all.sh`: one configuration at a time, 120 s pause before each, stops a configuration at once if a container fails to start, flags runs that end too early or had refused connections; output to `~/sde/out_<configuration>.txt` | Used for all final runs |

The override files contain the absolute path `/home/juhic/sde/...`; see the README for how to change it.

## Analysis additions (not changes to the authors' files)

- `process_logs.py` reads HWiNFO logs (`D:\SDE_results\hwinfo*.csv`, cp1252, date `d.m.yyyy`, time `H:M:S.ms`) and adds `power_w` and `energy_j` per trial: mean **CPU Package Power** over the 110 s after the trial's first request x 110 s. Needs at least 88 of the 110 one-second samples; otherwise empty. Tested on the user's real HWiNFO file (HP Victus, i5-13420H: 85 samples, 8.45 W idle) and on synthetic logs (10 W gives exactly 1100 J).
- HWiNFO's "Total System Power" read a constant 0.32 W on this laptop, so it is not used. There is no DRAM power sensor, unlike the paper's PowerStat (CPU + DRAM).
- `stats.py` drops trials where a Locust process did not start, then runs Mann-Whitney + Holm + Cliff's delta and OLS on `energy_j` and `cpu_cores` as well as response time. It also prints the actual requests per second per configuration.
- Added for the final analysis: `per_system_ols.py` (per-system OLS with users × granularity interaction, because the pooled model confounds granularity with system), `compare_paper_energy.py` (RQ1 next to the paper's Table V/VI, with and without the paper's IQR outlier filter) and `plot_by_load.py` (energy and response time vs. load, `fig_by_load.png/.pdf`).
