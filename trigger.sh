# This is main script to trigger edgex-taf tests in non-docker mode in pipeline or local environment
#	usage for KVM: sh trigger.sh --service functionalTest/V2-API/core-metadata --auth admin/admin --port 8002 --target KVM --path <Path_of_edge-linux-test-pytest>
#	usage for STM: sh trigger.sh --service functionalTest/V2-API/core-metadata --auth admin/admin --port 8002 --target STM --ip <IP_address_of_STM> --path <Path_of_edge-linux-test-pytest>
#
# This script workflow will be like
#       1. Parse arguments
#              Note: if you will set target as KVM then no need to give IP address.
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
    echo "Usage: sh trigger.sh --service functionalTest/V2-API/<any_service> --auth <username/password> --port <port_number> --target <Target_device> --ip <ip_address> --path <Path_of_edge-linux-test-pytest>"
    exit 1
fi

SHORT=s:,a:,p:,t:,i:,P:
LONG=service:,auth:,port:,target:,ip:,path:
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
    -t | --target)
      target=$2
      shift 2
      ;;
    -i | --ip)
      ip=$2
      shift 2
      ;;
    -P | --path)
      path=$2
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
export WORK_DIR=`pwd`
export DATA_DIR=${WORK_DIR}/working_dir/${data_dir}
export DATA_FILE=${DATA_DIR}/data.txt
export SECURITY_SERVICE_NEEDED=true
export DEPLOY_TYPE=manual
export AUTH=${auth}
export PORT=${port}
export TARGET=${target}

if [ $target == "KVM" ] || [ $target == "kvm" ]
then
    if [ "$path" ] # will check if user will provide path for edge-linux-test-pytest repo
    then
        if [ ! -d "$path" ]
        then
            echo "Can not find edge-liux-test-pytest repo path"
            exit 1
        else
            export PYTEST_PATH=${path}
        fi
    else # if user did not provide path then will check default path
        if [ ! -d "../edge-linux-test-pytest/" ]
        then
            echo "Can not find edge-linux-test-pytest repo default path"
            exit 1
        else
            path="${WORK_DIR}/../edge-linux-test-pytest"
            export PYTEST_PATH=${path}
       fi
    fi
fi

if [ $target == "STM" ] || [ $target == "stm" ]
then
    echo $ip > $DATA_FILE
fi

# creating VENV if it does not exist
if [ ! -d "env_taf" ]
then
    version=$(python3 -V)
    if [ "$version" != "Python 3.8.10" ]
    then
        echo "Require Python 3.8.10"
        exit 1
    fi
    echo "=============="
    echo "creating VENV"
    echo "=============="
    rm -rf ~/.cache/pip
    python3 -m venv env_taf
    source env_taf/bin/activate
    timeout 2m python3 -m pip install -U pip
    result=`echo $?`
    if [ $result != 0 ]
    then
        echo "Timeout while creating virtual environment !!!"
        exit 1
    fi
else
    source env_taf/bin/activate
fi

# Install Robot Framework related Libraries
echo "<<<<< Installing Robot framework related libraries >>>>>"
timeout 2m pip3 install -r requirements.txt --use-pep517
result=`echo $?`
if [ $result != 0 ]
then
    echo "Timeout while Installing Robot Framework related Libraries !!!"
    exit 1
fi
sleep 1

if [ ! -d "edgex-taf-common" ]
then
    # Install TAF common:
    echo "<<<<< Installing TAF common >>>>>"
    git clone https://github.com/edgexfoundry/edgex-taf-common.git
    sleep 1
    # Install dependency lib
    echo "<<<<< Installing TAF common related libraries >>>>>"
    timeout 2m pip3 install -r ./edgex-taf-common/requirements.txt --use-pep517
    result=`echo $?`
    if [ $result != 0 ]
    then
        echo "Timeout while Installing TAF common related libraries !!!"
        exit 1
    fi

    # Install edgex-taf-common as lib
    timeout 2m pip3 install ./edgex-taf-common --use-pep517
    result=`echo $?`
    if [ $result != 0 ]
    then
        echo "Timeout while Installing edgex-taf-common !!!"
        exit 1
    fi
fi

if [ ! -f ${WORK_DIR}/working_dir/status.txt ]
then
    # Change general modification as well as service specific modification for test execution
    python3 prerequisite_changes.py ${test_service} ${target}

    result=`echo $?`
    if [ $result != 0 ]
    then
        echo "Something went wrong."
        exit 1
    fi
    echo done > ${WORK_DIR}/working_dir/status.txt
fi

# Deploy edgex
timeout 5m python3 -m TUC --exclude Skipped --include deploy-base-service -u deploy.robot -p default
result=`echo $?`
if [ $result != 0 ]
then
    echo "Timeout !!!"
    echo "Failed to deploy edgex. Exit from script"
    exit 1
fi

cp TAF/testArtifacts/reports/edgex/log.html ${DATA_DIR}/deploy.html
while [ ! -f ${DATA_DIR}/data.txt ]
do
    sleep 1
done

# Start test case execution
timeout 10m python3 -m TUC --exclude Skipped -t $service -p default
result=`echo $?`
if [ $result != 0 ]
then
    echo "Timeout while executing Test suite!!!"
    exit 1
fi

while [ ! -f TAF/testArtifacts/reports/edgex/log.html ]
do
   sleep 1
done

# saving logs
cp TAF/testArtifacts/reports/edgex/log.html ${DATA_DIR}

# Shutdown edgex
timeout 2m python3 -m TUC --exclude Skipped --include shutdown-edgex -u shutdown.robot -p default
result=`echo $?`
if [ $result != 0 ]
then
    echo "Timeout !!!"
    echo "Failed to shutdown edgex. Exit from script"
    exit 1
fi
cp TAF/testArtifacts/reports/edgex/log.html ${DATA_DIR}/shutdown.html

if [ $VIRTUAL_ENV ]
then
    # deactivate VENV
    deactivate
fi
