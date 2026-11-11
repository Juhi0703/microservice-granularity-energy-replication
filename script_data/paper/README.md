# Experimental Setup

The experiment requires two separate servers:

## Microservices Server
This server hosts the microservices applications and handles power consumption measurements.

### Hardware Requirements
- Intel processor with **RAPL** (Running Average Power Limit) support (Sandy Bridge architecture or newer)
- Linux-compatible hardware with ACPI (Advanced Configuration and Power Interface) support

### Software Requirements
- Linux-based operating system (Ubuntu recommended)
- Linux kernel 3.13 or newer
- Docker and Docker Compose
- Root access privileges
- PowerStat for power consumption monitoring

## Load Testing Server
This server is dedicated to running performance tests.

### Software Requirements
- Python installation

The experiment can be recreated by following these four steps:


## Docker compose
Here's how to run the Docker Compose configuration:

1. Locate the Docker Compose File
   - There are two systems in the /experiment folder: /pet_system, /train_system. Navigate to the system folder that you want to run the experiments. 
   - Each system has three granularity folders: /coarse, /medium, /fine
   - Find the appropriate `docker-compose.yml` file in the corresponding granularity folder. For example if you want to run the experiment for the fine-grained Train Ticket system, you can navigate to the experiment/train_system/fine folder and run the docker-compose.yml file.
   

2. Server Deployment
   - Transfer the selected `docker-compose.yml` file to your target server
   - Ensure you have proper permissions for file transfer and execution
   - run 'docker-compose up' in the terminal  

These source code repositories contain detailed documentation and implementation details that can help resolve any setup issues.

## Load Testing
To perform load testing, follow these steps:

1. Deploy the Environment
   - Execute the `docker-compose` file on your target server
   - This will set up the necessary testing environment

2. Configure Port Settings
   - Update the port configurations in your testing scripts to match the server's ports
   - Example: For testing the per-clinic system's coarse granularity on server 11.22.33.44:
     - Navigate to `/pet_system/coarse`
     - Modify the IP address to point to 11.22.33.44

3. Set Up Results Storage
   - Locate the folder name parameter in your testing script
   - Update it to match your server's designated results directory
   - This ensures all test results are saved in the correct location

4. Run the Load Test
   - Locate the testing script in the granularity folder
   - Execute the testing script on your local machine 
   
This setup ensures proper execution of load tests and accurate result collection.

## Energy measurement

To measure energy consumption, follow these steps:

1. Download the Energy Measurement Tool
   - Download the energy measurement tool from the following link: [https://github.com/ColinIanKing/powerstat] 

2. Put the power.sh file on the server
   - The power.sh can be found in the /experiment/measurement_script/
   - Transfer the `power.sh` file to the server where you want to measure energy consumption
   - Ensure you have the necessary permissions to execute the script

3. Run the Energy Measurement Tool


## Data Analysis

The data and the dats analysis script of our paper can be found in the folder: /data_and_data_analysis/. Due to the size of the dataset, the data has been compressed.

In the /data_and_data_analysis/data folder, you can found the data from the load testing tool and the energy measurement tool.

In the /data_and_data_analysis/data_analysis/script, you can found the data analysis script. In the /data_and_data_analysis/data_analysis/figure, you can found the figure from the script.


## DEBUG
- Due to the setting of the SQL, there are maybe some small errors in the train-ticket system. To fix this, you can check the log of the consign-price service in the train-ticket system,
  and then you can find the error message in the log. You can fix the error by changing the id of the task23 in the script of the train-ticket system.