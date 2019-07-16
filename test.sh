#!/usr/bin/env bash
help (){
    echo "options"
    echo "-c (flag) clear score, state db if this flag on"
    echo "-d (flag) decentalize if this flag on"
    exit 0
}

clearFlag=0
decentralizationFlag=0

while getopts "rcd" opt
do
    case "$opt" in
        c) clearFlag=1;;
        d) decentralizationFlag=1;;
        h) help;;
    esac
done

tbears stop

if [[ ${clearFlag} -eq 1 ]];then
    tbears clear
fi
tbears start

pytest test_suite/init_test.py

if [[ ${decentralizationFlag} -eq 1 ]];then
    pytest test_suite.json_rpc_api.decentralized.test_decentralization0.py
fi

pushd test_suite/json_rpc_api
pytest --ignore=decentralized --ignore=pre_vote
popd

cp -r .score/ .score2/
cp -r .statedb/ .statedb2/

