# Test script for the fine_depre-grained pet microservice system
from locust import HttpUser, TaskSet, task, between, events, constant_pacing
import random
import logging
from datetime import datetime
import os
import threading
import argparse
import inspect

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
results_dir = 'results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
log_filename = os.path.join(results_dir, f'locust_requests_{timestamp}.log')
logger = logging.getLogger('locust')
limit = 200
pacing = 1


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    if exception:
        logger.error(f'FAILURE: {request_type} {name} {response_time}ms {exception}')
    else:
        logger.info(f'SUCCESS: {request_type} {name} {response_time}ms {response_length} bytes')


class AllTasks(TaskSet):
    @task
    def customer_task_1(self):
        self.client.get("customer/owners")

    @task
    def customer_task_2(self):
        id = random.randint(1, 10)
        self.client.get(f"customer/owners/{id}")

    @task
    def pets_task_1(self):
        self.client.get("pet/petApi/petTypes")

    @task
    def pets_task_2(self):
        id = random.randint(1, 8)
        self.client.get(f"pet/petApi/owners/1/pets/{id}")

    @task
    def vets_task_1(self):
        id = random.randint(1, 6)
        first_name = random.choice(["James", "Helen", "Linda", "Michael", "Mary", "John"])
        last_name = random.choice(["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis"])
        data = {
            "firstName": first_name,
            "lastName": last_name
        }
        self.client.post(f"vet/vets/Update/{id}", json=data)

    @task
    def vets_task_2(self):
        id = random.randint(1, 6)
        self.client.get(f"vet/vets/vets/{id}")

    @task
    def vets_task_3(self):
        self.client.get("vet/vets")

    @task
    def visits_task_1(self):
        self.client.get("visit/visits/visits")

    @task
    def visits_task_2(self):
        id = random.randint(1, 6)
        data = {
            "date": "2022-01-01",
            "description": "Test visit",
            "petId": id
        }
        self.client.post(f"visit/visits/visits/update/{id}", json=data)

    @task
    def visits_task_3(self):
        id = random.randint(1, 6)
        self.client.get(f"visit/visits/pets/visits/{id}")


class PetClinicUser(HttpUser):
    tasks = [AllTasks]
    wait_time = constant_pacing(pacing)
    host = "http://localhost:8080/api/"


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
        "-u", str(args.users),
        "-r", str(args.rate),
        "--run-time", args.run_time,
        "--csv=locust_report",
        f"--logfile=result05/fine/locustfile_{pacing}_{args.users}_{args.rate}_{args.run_time}_{args.iteration}.log"
    ]

    print("Executing command:")
    print(" ".join(command))

    os.system(" ".join(command))