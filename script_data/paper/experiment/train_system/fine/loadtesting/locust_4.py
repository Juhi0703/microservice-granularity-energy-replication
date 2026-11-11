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
    def get_request31(self):
        self.client.get("http://localhost:18856/api/v1/foodservice/orders")

    @task
    def get_request32(self):
        self.client.get("http://localhost:18673/api/v1/inside_pay_service/inside_payment/account")

    @task
    def get_request33(self):
        travelDate = "2013-08-09"
        trainNumber = "1"
        self.client.get(f"http://localhost:12034/api/v1/orderOtherService02/orderOther/{travelDate}/{trainNumber}")

    @task
    def get_request34(self):
        self.client.get("http://localhost:19001/api/v1/paymentservice/payment")

    @task
    def get_request35(self):
        self.client.get("http://localhost:14568/api/v1/preserveservice/welcome")

    @task
    def get_request36(self):
        info = {
                  "date": "string",
                  "loginId": "string",
                  "oldTripId": "string",
                  "orderId": "string",
                  "seatType": 0,
                  "tripId": "string"
              }
        self.client.post("http://localhost:18886/api/v1/rebookservice/rebook/difference", json=info)


    @task
    def get_request37(self):
        self.client.get("http://localhost:17525/api/v1/waitorderservice/orders")

    @task
    def post_request38(self):
        data = {
            "departureTime": "2013-08-12",
            "endPlace": "shanghai",
            "startPlace": "nanjing"
        }
        self.client.post("http://localhost:14322/api/v1/travelplanservice/travelPlan/cheapest", json=data)

    @task
    def post_request39(self):
        data = {
            "endStation": "shanghai",
            "num": 0,
            "startStation": "nanjing",
            "travelDate": "2013-08-01"
        }
        self.client.post("http://localhost:14578/api/v1/routeplanservice/routePlan/cheapestRoute", json=data)

    @task
    def get_request40(self):
        self.client.get("http://localhost:14569/api/v1/preserveotherservice/welcome")

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
