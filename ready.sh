#!/usr/bin/env bash
help() {
    echo "options"
    echo "-d (flag) decentralize"
    exit 0
}

tbears stop
tbears clear
tbears start

pytest test_suite/init_test.py
decentralizationTestFlag=0
while getopts "hd" opt
do
    case "$opt" in
        d) decentralizationTestFlag=1;;
        h) help ;;
    esac
done

if [[ "$decentralizationTestFlag" -eq 1 ]];then
    pytest test_suite/json_rpc_api/decentralized/test_decentralization0.py
fi

cp -rf .score/ .score2/
cp -rf .statedb/  .statedb2/