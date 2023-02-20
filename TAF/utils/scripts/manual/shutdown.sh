# This script is to shutdown edgex after executing test cases

#!/bin/sh

cd ${WORK_DIR}/../edge-linux-test-pytest
GLOBAL_VAR_DIR=${WORK_DIR}/TAF/config/global_variables.py

if [ -f kvm_data.json ]
then
    pid=`jq '.pid' kvm_data.json`
    kill -9 ${pid}
    rm kvm_data.json

    sed -i '0,/BASE_URL = .*/ s//BASE_URL = ""/' $GLOBAL_VAR_DIR
else
    echo ""
    echo "###################"
    echo "KVM is already down"
    echo "###################"
    echo ""
fi
