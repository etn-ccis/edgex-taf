# This script will generate X-Auth-Token

#!/bin/bash

option=${1}
BASE_URL=`cat ${DATA_DIR}/data.txt`

if [ -z "$AUTH" ]
then
    username="admin"
    password="admin"
else
    username=`echo ${AUTH} |cut -d/ -f 1`
    password=`echo ${AUTH} |cut -d/ -f 2`
fi

port=${PORT}

case ${option} in
  -useradd)  #create user
    if [ -z "$token" ]
    then
        token=`curl -s -X POST "https://${BASE_URL}:${port}/login" -H  "accept: application/json" -H  "X-Original-IP: ${BASE_URL}" -H  "Content-Type: application/json" -d "{\"username\":\"${username}\",\"password\":\"${password}\"}" --insecure | jq -r .token`
        echo ${token}
    else
        echo ${token}
    fi
  ;;
  -userdel)  #delete user
    token=''
    echo ${token}
  ;;
esac
