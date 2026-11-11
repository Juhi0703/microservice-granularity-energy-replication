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
    def get_request21(self):
        self.client.get("http://localhost:18888/api/v1/assuranceservice/assurances")

    @task
    def get_request22(self):
        self.client.get("http://localhost:15679/api/v1/configservice/configs")

    @task
    def post_request23(self):
        price = {
            "beyondPrice": 1,
            "id": "a36e31a1-0402-4cd3-aac2-50764da4add0",
            "index": 0,
            "initialPrice": 2,
            "initialWeight": 1,
            "withinPrice": 2
        }
        self.client.post("http://localhost:16110/api/v1/consignpriceservice/consignprice", json=price)

    @task
    def get_request24(self):
        id = "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f"
        self.client.get(f"http://localhost:16111/api/v1/consignservice/consigns/account/{id}")
    @task
    def get_request25(self):
        self.client.get("http://localhost:17853/api/v1/notifyservice/test_send_mq")

    @task
    def get_request26(self):
        self.client.get("http://localhost:11188/api/v1/securityservice/securityConfigs")

    @task
    def get_request27(self):
        tripId = "G1234"
        self.client.get(f"http://localhost:12346/api/v1/travelservice/train_types/{tripId}")

    @task
    def get_request28(self):
        orderId = "95575bcc-7f64-42ce-a21a-832641b57f85"
        #self.client.get("http://localhost:18885/api/v1/cancelservice/welcome")
        self.client.get("http://localhost:18885/api/v1/cancelservice/cancel/95575bcc-7f64-42ce-a21a-832641b57f85/1")


    @task
    def get_request29(self):
        orderId = "95575bcc-7f64-42ce-a21a-832641b57f85"
        #self.client.get(f"//localhost.12386/api/v1/executeservice/execute/collected/{orderId}")
        self.client.get("http://localhost:12386/api/v1/executeservice/welcome")

    @task
    def get_request30(self):
        self.client.get("http://localhost:18957/api/v1/fooddeliveryservice/orders/all")


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
        f"--logfile=result05/fine/locustfile_{pacing}_{args.users}_{args.rate}_{args.run_time}_{args.iteration}.log"
    ]
    os.system(" ".join(command))
