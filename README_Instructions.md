# EdgeX-TAF execution in Pipeline as well as local environment

This is created as an intro to understand how EdgeX-TAF will be execute in pipeline or local environment

# How to Run

  1. In Pipeline
      * Run command:
        **sh trigger.sh --service functionalTest/V2-API/<service_name> --auth <username/password> --port <port_number> --target <target_device_under_test> --ip <IP_address> --path <path_of_edge-linux-test_pytest_repo>**

  2. In Local System
      * Remove "--yocto --conn_method=http" from TAF/utils/scripts/manual/deploy-edgex.sh file 
        so line should be like "python3 px_red/target/utilities/start_kvm.py &> kvm.log &" then 
        run command:
	**sh trigger.sh --service functionalTest/V2-API/<service_name> --auth <username/password> --port <port_number> --target <target_device_under_test> --ip <IP_address> --path <path_of_edge-linux-test_pytest_repo>**


## trigger.sh

This is main script which will be triggered from pipeline. To run this script user will need to have python 3.8.10 version

user will need to run script as below from pipeline or local system

sh trigger.sh --service functionalTest/V2-API/<service_name> --auth <username/password> --port <port_number> --target <target_device_under_test> --ip <IP_address> --path <path_of_edge-linux-test_pytest_repo>

   * service_name: this will be service name which is present under V2-API
   * username/password: this will be username and password of board. if user will not provide then it will
                        take default as admin/admin
   * port: this is edgex client port. as of now we will take as 8002
   * target: this will be any target device like KVM or STM
   * ip: this will be IP address of target device. if you give target name as KVM then there is no need to provide IP adress
   * path: If target is KVM then user will need to give a specific path of "edge-linux-test-pytest" repo. if user will not give path then script will take default path as "${WORK_DIR}/../edge-linux-test-pytest".
           If user will give wrong path then script will not execute.


The execution flow of this script will be as follow
   1. Parse arguments
   2. Create unique directory to store logs and data (Here we are creating one data.txt file while deploying edgex which contains IP address of target which will needed while creating X-Auth-Token and restarting or stop any service)
   3. Check existance of virtualenv and if not exist then will create it
   4. call prerequisite_changes.py file to make changes according to service
   5. deploy edgex
   6. start run test suite and save logs under unique directory
   7. shutdown edgex

## prerequisite_changes.py

This file contains required modification to be done in EdgeX-TAF before execution start


## There are some more scripts which are under TAF/utils/scripts/manual/ directory and will be use for non docker environment execution.

##### 1. api-gateway-token.sh
         In non docker mode we are using X-Auth method. So, this script is used to create X-Auth-Token with curl command. 
         Here this script will be called while testsuite setup, teardown and execution of robot tests.

##### 2. deploy-edgex.sh
         This is first script which will be called to deploy edgex when we start execution. So basically if our target device will be KVM 
         then it will start QEMU and set IP address of QUMU to BASE_URL in global_variables.py file. If target device will other devices 
         then directly it will set IP address of device to BASE_URL in global_variables.py file.
         (Note: if execution will be in local environment then remove "--yocto --conn_method=http" from this file. so line should be like 
                "python3 px_red/target/utilities/start_kvm.py &> kvm.log &")

##### 3. shutdown.sh
         This script is the last script which will shutdown edgex and do some cleanup task.

##### 4. restart-services.sh
         This script is used to restart any micro service.

##### 5. stop-services.sh
         This script is used to stop any micro service.


## Additional information:
Have added Virtual-Sample-Profile.yaml in location: TAF/testData/core-metadata/deviceprofile/Virtual-Sample-Profile.yaml
which is needed for core-command testing.