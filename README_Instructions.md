# EdgeX-TAF execution in Pipeline

This is created as an intro to understand how EdgeX-TAF will be executed in pipeline

## trigger.sh

This is main script which will be triggered from pipeline.

user will need to run script as below from pipeline

sh trigger.sh --service functionalTest/V2-API/<service_name> --auth <username/password> --port <port_number> --module <module> --ip <IP_address>

   * service_name: this will be service name which is present under V2-API
   * username/password: this will be username and password of board. if user will not provide then it will
                        take default as admin/admin
   * port: this is socket port. as of now we will take as 8002
   * module: this will be any module like KVM or STM
   * ip: this will be IP address of modue. if you give module name as KVM then there is no need to provide IP adress


The execution flow of this script will be as follow
   1. Parse arguments
   2. Create unique directory to store logs and data
   3. Check existance of virtualenv and if not exist then will create it
   4. call prerequisite_changes.py file to make changes according to service
   5. deploy edgex
   6. start run test suite and save logs under unique directory
   7. shutdown edgex

## prerequisite_changes.py

This file contains required modification to be done in EdgeX-TAF before execution start
