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
    def post_request_1(self):
        name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))
        payload = {
            "id": "string",
            "name": name,
            "stayTime": 2
        }
        self.client.post("http://localhost:12345/api/v1/stationservice/stations", json=payload)

    @task
    def get_request_2(self):
        self.client.get("http://localhost:16579/api/v1/priceservice/prices")

    @task
    def get_request_3(self):
        self.client.get("http://localhost:19999/api/v1/trainfoodservice/trainfoods")

    @task
    def get_request_4(self):
        self.client.get("http://localhost:14567/api/v1/trainservice/trains")

    @task
    def get_request_5(self):
        self.client.get("http://localhost:11178/api/v1/routeservice/routes")

    @task
    def get_request_6(self):
        self.client.get("http://localhost:12347/api/v1/contactservice/contacts")

    @task
    def get_request_7(self):
        self.client.get("http://localhost:18767/api/v1/adminbasicservice/adminbasic/contacts")

    @task
    def get_request_8(self):

        self.client.get("http://localhost:18769/api/v1/adminbasicservice03/adminbasic/configs")

    @task
    def get_request_9(self):
        self.client.get("http://localhost:16112/api/v1/adminorderservice/adminorder")

    @task
    def get_request_10(self):
        cities = ["beijing", "shanghai", "xuzhou", "hangzhou"]
        city = random.choice(cities)
        self.client.get(f"http://localhost:15680/api/v1/basicservice/basic/{city}")


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
