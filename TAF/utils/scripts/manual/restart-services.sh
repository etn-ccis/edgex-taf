# This script is to restart any service

#!/bin/sh

BASE_URL=`cat ${DATA_DIR}/data.txt`
SERVICE=$1

if [ -z "$AUTH" ]
then
    username="admin"
    password="admin"
else
    username=`echo ${AUTH} |cut -d/ -f 1`
    password=`echo ${AUTH} |cut -d/ -f 2`
fi

echo ${password} > ${DATA_DIR}/password.txt
sshpass -f ${DATA_DIR}/password.txt ssh -t ${username}@${BASE_URL} 'echo ${password}|sudo -S systemctl restart '${SERVICE}''
sleep 2
rm ${DATA_DIR}/password.txt
