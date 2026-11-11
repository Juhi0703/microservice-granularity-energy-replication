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
    def task_31(self):
        self.client.get("http://localhost:18856/api/v1/foodservice/orders")

    @task
    def task_32(self):
        self.client.get("http://localhost:18673/api/v1/inside_pay_service/inside_payment/account")

    @task
    def task_33(self):
        travelDate = "2013-08-09"
        trainNumber = "1"
        self.client.get(f"http://localhost:18673/api/v1/orderOtherService/orderOther/{travelDate}/{trainNumber}")

    @task
    def task_34(self):
        self.client.get("http://localhost:17853/api/v1/paymentservice/payment")

    @task
    def task_35(self):
        self.client.get("http://localhost:18856/api/v1/preserveservice/welcome")

    @task
    def task_36(self):
        self.client.get("http://localhost:17525/api/v1/rebookservice/welcome")

    @task
    def task_37(self):
        self.client.get("http://localhost:17525/api/v1/waitorderservice/orders")

    @task
    def task_38(self):
        data = {
            "departureTime": "2013-08-12",
            "endPlace": "shanghai",
            "startPlace": "nanjing"
        }
        self.client.post("http://localhost:12345/api/v1/travelplanservice/travelPlan/cheapest", json=data)

    @task
    def task_39(self):
        data = {
            "endStation": "shanghai",
            "num": 0,
            "startStation": "nanjing",
            "travelDate": "2013-08-01"
        }
        self.client.post("http://localhost:12346/api/v1/routeplanservice/routePlan/cheapestRoute", json=data)

    @task
    def task_40(self):
        self.client.get("http://localhost:18673/api/v1/preserveotherservice/welcome")

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
