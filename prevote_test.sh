#!/usr/bin/env bash

help() {
    echo "options"
    echo "-c (flag) clear score, state db if this flag on"
    exit 0
}
clearFlag=0
while getopts "hc" opt
do
    case "$opt" in
        c) clearFlag=1;;
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
cp -rf .score/ .score2/
cp -rf .statedb/ .statedb2/
