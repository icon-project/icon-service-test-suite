#!/usr/bin/env bash

help() {
    echo "options"
    echo "-n test_no (specific decentralization tests. default=test_decentralization0.py)"
    echo "-r (flag) stop tbears server if this flag on"
    echo "-c (flag) clear score, state db if this flag on"
    exit 0
}
n=0
clearFlag=0
restartFlag=0
while getopts "n:hcr" opt
do
    case "$opt" in
        n) n=$OPTARG;;
        c) clearFlag=1;;
        r) stopFlag=1;;
        h) help ;;
    esac
done

tbears stop
if [[ ${clearFlag} -eq 1 ]];then
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

if [[ ${restartFlag} -eq 1 ]];then
    tbears start
fi
