# This script is to shutdown edgex after executing test cases

#!/bin/sh

cd ${WORK_DIR}/../edge-linux-test-pytest
GLOBAL_VAR_DIR=${WORK_DIR}/TAF/config/global_variables.py

if [ -f kvm_data.json ]
then
    pid=`jq '.pid' kvm_data.json`
    kill -2 ${pid}
    result=`echo $?`

    if [ $result = "1" ]
    then
        echo "<<<< Edgex shutdown failed >>>>"
    else
        rm kvm_data.json
        sed -i '0,/BASE_URL = .*/ s//BASE_URL = ""/' $GLOBAL_VAR_DIR
        echo "<<<< Edgex shutdown successfully >>>>"
    fi
else
    echo ""
    echo "###################"
    echo "KVM is already down"
    echo "###################"
    echo ""
fi
