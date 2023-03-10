# This script is to deploy KVM and get IP address of qemu

#!/bin/bash

GLOBAL_VAR_DIR=${WORK_DIR}/TAF/config/global_variables.py

if [ ${TARGET} ==  "KVM" ] || [ ${TARGET} ==  "kvm" ]
then
    #cd ${WORK_DIR}/../edge-linux-test-pytest
    cd ${PYTEST_PATH}
    echo "<<<<< Installing pytest related libraries >>>>>"
    timeout 2m pip3 install -r ${HOME}/edge-linux-test-pytest/requirements.txt --use-pep517
    result=`echo $?`
    if [ $result != 0 ]
    then
        echo "Timeout while installing pytest related libraries !!!"
        exit 1
    fi

    if ps ax | grep -v grep | grep start_kvm.py > /dev/null
    then
        echo "#################"
        echo "KVM is already up"
        echo "#################"
    else
        if [ -f kvm_data.json ]
        then
            rm kvm_data.json
        fi

        if [ -f ${DATA_DIR}/data.txt ]
        then
            rm ${DATA_DIR}/data.txt
        fi

        python3 px_red/target/utilities/start_kvm.py --yocto --conn_method=http &> kvm.log &

        while [ ! -f kvm_data.json ]
        do
            sleep 1
        done

        ip=`jq '.ip_address' kvm_data.json`
        echo ${ip} >> ${DATA_DIR}/data.txt
        sed 's/.//;s/.$//' ${DATA_DIR}/data.txt > ${DATA_DIR}/data1.txt
        mv ${DATA_DIR}/data1.txt ${DATA_DIR}/data.txt
        sed -i '0,/BASE_URL = .*/ s//BASE_URL = '$ip'/' $GLOBAL_VAR_DIR
    fi
else
    ip=`cat ${DATA_FILE}`
    sed -i '0,/BASE_URL = .*/ s//BASE_URL = "'$ip'"/' $GLOBAL_VAR_DIR
fi
