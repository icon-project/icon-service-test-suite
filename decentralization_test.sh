#!/usr/bin/env bash

help() {
    echo "-n test_no (specific decentralization tests. default=test_decentralization1.py)"
    exit 0
}
n=0
flag=0
while getopts "n:hc" opt
do
    case $opt in
        n) n=$OPTARG;;
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
pushd test_suite/json_rpc_api/decentralized
pytest test_decentralization"$n".py
tbears stop
popd
cp -r .score/ .score2/
cp -r .statedb/ .statedb2/
