#!/usr/bin/env bash

help() {
    echo "options"
    echo "-r (flag) stop tbears server if this flag on"
    echo "-c (flag) clear score, state db if this flag on"
    exit 0
}
clearFlag=0
restartFlag=0
while getopts "hcr" opt
do
    case "$opt" in
        c) clearFlag=1;;
        r) restartFlag=1;;
        h) help ;;
    esac
done

tbears stop

if [[ ${clearFlag} -eq 1 ]];then
    tbears clear
fi
tbears start

pytest test_suite/init_test.py
pushd test_suite/json_rpc_api/pre_vote
pytest
tbears stop
popd
cp -r .score/ .score2/
cp -r .statedb/ .statedb2/

if [[ ${restartFlag} -eq 1 ]];then
    tbears start
fi
