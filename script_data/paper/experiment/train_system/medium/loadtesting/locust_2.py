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
    def get_request_11(self):
        self.client.get("http://localhost:12031/api/v1/orderservice/order")

    @task
    def get_request12(self):
        orderId = "9bb0ac3e-b305-4929-84a9-2dfac9de3471"
        self.client.get(f"http://localhost:12031/api/v1/orderservice/order/{orderId}")

    @task
    def get_request13(self):
        self.client.get("http://localhost:12032/api/v1/orderOtherService/orderOther")

    @task
    def get_request14(self):
        seat = {
                  "destStation": "string",
                  "seatType": 0,
                  "startStation": "string",
                  "stations": [
                    "string"
                  ],
                  "totalNum": 0,
                  "trainNumber": "string",
                  "travelDate": "string"
            }
        #self.client.post("http://localhost:18898/api/v1/seatservice/left_tickets", json=seat)
        self.client.get("http://localhost:18898/api/v1/seatservice/welcome")

    @task
    def get_request15(self):
        cities = ["beijing", "shanghai", "nanjing", "hangzhou"]
        self.client.get("http://localhost:12345/api/v1/stationfoodservice/stationfoodstores", json=cities)

    @task
    def get_request16(self):
        self.client.get("http://localhost:16346/api/v1/travel2service/trips")

    @task
    def get_request17(self):
        password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz123456', k=7))
        user = {
            "documentNum": "2135488099312X",
            "documentType": 1,
            "email": "trainticket_notify@163.com",
            "gender": 1,
            "password": password,
            "userId": "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
            "userName": "fdse_microservice"
        }
        self.client.put("http://localhost:12346/api/v1/userservice/users", json=user)

    @task
    def get_request18(self):
        self.client.get("http://localhost:17525/api/v1/admintravelservice/admintravel")

    @task
    def get_request19(self):
        self.client.get("http://localhost:16113/api/v1/adminrouteservice/adminroute")

    @task
    def get_request20(self):
        self.client.get("http://localhost:18888/api/v1/adminuserservice/users")




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
        f"--logfile=result05/medium/locustfile_{pacing}_{args.users}_{args.rate}_{args.run_time}_{args.iteration}.log"
    ]
    os.system(" ".join(command))
