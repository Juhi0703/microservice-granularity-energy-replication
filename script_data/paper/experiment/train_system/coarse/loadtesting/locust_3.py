# Test script for the fine_depre-grained train-ticketing microservice system
from locust import HttpUser, TaskSet, task, between, events, constant_pacing
import random
import logging
from datetime import datetime
import os
import threading
import argparse

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
results_dir = 'results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
log_filename = os.path.join(results_dir, f'locust_requests_{timestamp}.log')

logger = logging.getLogger('locust')
pacing = 1

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    if exception:
        logger.error(f'FAILURE: {request_type} {name} {response_time}ms {exception}')
    else:
        logger.info(f'SUCCESS: {request_type} {name} {response_time}ms {response_length} bytes')


class StationServiceTask(TaskSet):

    @task
    def task_21(self):
        self.client.get("http://localhost:18888/api/v1/assuranceservice/assurances")

    @task
    def task_22(self):
        self.client.get("http://localhost:12347/api/v1/configservice/configs")

    @task
    def task_23(self):
        price = {
            "beyondPrice": 1,
            "id": "869d9d5e-1940-438a-8f0f-7c23d75d9ed5",
            "index": 0,
            "initialPrice": 2,
            "initialWeight": 1,
            "withinPrice": 2
        }
        self.client.post("http://localhost:12347/api/v1/consignpriceservice/consignprice", json=price)

    @task
    def task_24(self):
        id = "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f"
        self.client.get(f"http://localhost:12347/api/v1/consignservice/consigns/account/{id}")
    @task
    def task_25(self):
        self.client.get("http://localhost:17853/api/v1/notifyservice/test_send_mq")

    @task
    def task_26(self):
        self.client.get("http://localhost:14567/api/v1/securityservice/securityConfigs")

    @task
    def task_27(self):
        tripId = "G1234"
        self.client.get(f"http://localhost:12346/api/v1/travelservice/train_types/{tripId}")

    @task
    def task_28(self):
        self.client.get("http://localhost:18888/api/v1/cancelservice/welcome")

    @task
    def task_29(self):
        self.client.get("http://localhost:18856/api/v1/executeservice/welcome")

    @task
    def task_30(self):
        self.client.get("http://localhost:18856/api/v1/fooddeliveryservice/orders/all")

class PetClinicUser(HttpUser):
    tasks = [StationServiceTask]
    wait_time = constant_pacing(pacing)
    host = "http://localhost"

if __name__ == "__main__":
    import os
    import sys


    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--users", type=int, required=True, help="Number of users")
    parser.add_argument("-r", "--rate", type=int, required=True, help="Spawn rate")
    parser.add_argument("--run-time", type=str, required=True, help="Run time")
    parser.add_argument("--iteration", type=int, required=True, help="Iteration number")
    args = parser.parse_args()

    command = [
        sys.executable, "-m", "locust",
        "-f", __file__,
        "--headless",
        "-u", str(args.users),  # Number of users
        "-r", str(args.rate),  # Spawn rate
        "--run-time", args.run_time,
        "--csv=locust_report",
        f"--logfile=result05/coarse/locustfile_{pacing}_{args.users}_{args.rate}_{args.run_time}_{args.iteration}.log"
    ]
    os.system(" ".join(command))
