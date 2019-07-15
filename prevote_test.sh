#!/usr/bin/env bash

help() {
    echo " clear db if -c flag on "
    exit 0
}
flag=0
while getopts "hc" opt
do
    case $opt in
        c) flag=1;;
        h) help ;;
    esac
done

tbears stop
if [[ ${flag} -eq 1 ]];then
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