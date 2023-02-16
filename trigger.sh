# This is main script to trigger edgex-taf tests in non-docker mode in pipeline
#	usage for KVM: sh trigger.sh --service functionalTest/V2-API/core-metadata --auth admin/admin --port 8002 --module KVM
#	usage for STM: sh trigger.sh --service functionalTest/V2-API/core-metadata --auth admin/admin --port 8002 --module STM --ip <IP_address_of_STM>
#
# This script workflow will be like
#       1. Parse arguments
#              Note: if you will set module as KVM then no need to give IP address
#       2. Create unique directory to store logs and data
#	3. Check existance of virtualenv and if not exist then will create it.
#       4. call prerequisite_changes.py file to make changes according to service
#       5. deploy edgex
#       6. start run test suite and save logs under unique directory
#       7. shutdown edgex
#
# Note: After completion of test execution log report will be saved in working_dir/

#!/bin/bash

if [ $# -eq 0 ]
then
    echo "No arguments supplied, please provide data"
    echo "Usage: sh trigger.sh --service functionalTest/V2-API/<any_service> --auth <username/password> --port <port_number> --module <module> --ip <ip_address>"
    exit 1
fi

SHORT=s:,a:,p:,m:,i:
LONG=service:,auth:,port:,module:,ip:
OPTS=$(getopt -a -n weather --options $SHORT --longoptions $LONG -- "$@")

eval set -- "$OPTS"

while :
do
  case "$1" in
    -s | --service )
      service="$2"
      shift 2
      ;;
    -a | --auth )
      auth="$2"
      shift 2
      ;;
    -p | --port)
      port=$2
      shift 2
      ;;
    -m | --module)
      module=$2
      shift 2
      ;;
    -i | --ip)
      ip=$2
      shift 2
      ;;
    --)
      shift;
      break
      ;;
    *)
      echo "Unexpected option: $1"
      ;;
  esac
done

# parsing service name from functionalTest/V2-API/<core-service>
test_service=`echo $service | awk -F"/" '{print $NF}'`
service_flag=0

service_list=(core-data
              core-metadata
              core-command
              app-serice
              support-notifications
              support-schedular
              system-agent
             )

for str in ${service_list[@]}; do
  if [ $str == $test_service ]
  then
      service_flag=1
  fi
done

if [ $service_flag == 0 ]
then
    echo "Please provice valid service"
    exit 1
fi

#creating one timestamp based directory to store data
data_dir=$(date +%y%m%d_%H%M%S)
mkdir -p working_dir/${data_dir}

# export some variables before starting execution
export WORK_DIR=${HOME}/edgex-taf
export DATA_DIR=${WORK_DIR}/working_dir/${data_dir}
export DATA_FILE=${DATA_DIR}/data.txt
export SECURITY_SERVICE_NEEDED=true
export DEPLOY_TYPE=manual
export AUTH=${auth}
export PORT=${port}

if [ $module == "STM" ] || [ $module == "stm" ]
then
    echo $ip > $DATA_FILE
fi

# creating VENV if it does not exist
if [[ "$VIRTUAL_ENV" != " " ]]
then
    echo "=============="
    echo "creating VENV"
    echo "=============="
    python3 -m venv .
    source ./bin/activate
    python3 -m pip install -U pip
    pip install -U virtualenv
fi

# Install Robot Framework related Libraries
python3 -m pip install robotframework
python3 -m pip install requests
python3 -m pip install robotframework-requests
python3 -m pip install robotframework-jsonlibrary

# Install TAF common:
git clone https://github.com/edgexfoundry/edgex-taf-common.git

# Install dependency lib
pip3 install wheel
python3 -m pip install -r ./edgex-taf-common/requirements.txt
pip3 install pyyaml

# Install edgex-taf-common as lib
pip3 install ./edgex-taf-common

# Change general modification as well as service specific modification for test execution
python3 prerequisite_changes.py ${test_service} ${module}

result=`echo $?`

if [ $result = "1" ]
then
    exit 1
fi

if [ $module == "KVM" ] || [ $module == "kvm" ]
then
    # Deploy edgex
    python3 -m TUC --exclude Skipped --include deploy-base-service -u deploy.robot -p default

    while [ ! -f ${DATA_DIR}/data.txt ]
    do
        sleep 1
    done
fi

# Start test case execution
python3 -m TUC --exclude Skipped -t $service -p default

while [ ! -f TAF/testArtifacts/reports/edgex/log.html ]
do
   sleep 1
done

# saving logs
cp TAF/testArtifacts/reports/edgex/log.html ${DATA_DIR}

# Shutdown edgex
python3 -m TUC --exclude Skipped --include shutdown-edgex -u shutdown.robot -p default

# deactivate VENV
deactivate
