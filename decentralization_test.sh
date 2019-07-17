#!/usr/bin/env bash

help() {
    echo "options"
    echo "-n test_no (specific decentralization tests. default=test_decentralization0.py)"
    echo "-a (flag) tests all test after decentralize network"
    echo "-c (flag) clear score, state db if this flag on"
    echo "-d (flag) tests decentralization tests 0 to 6"
    exit 0
}
n=0
clearFlag=0
allFlag=0
decentralizationTestFlag=0
while getopts "n:hcad" opt
do
    case "$opt" in
        n) n=$OPTARG;;
        c) clearFlag=1;;
        a) allFlag=1;;
        d) decentralizationTestFlag=1;;
        h) help ;;
    esac
done

tbears stop
if [[ ${clearFlag} -eq 1 ]];then
    tbears clear
fi

if [[ ${decentralizationTestFlag} -eq 1 ]];then
    ./ready.sh
    testFiles=(`ls test_suite/json_rpc_api/decentralized | grep test_`)
    for testFile in ${testFiles[*]};do
        tbears start
        pushd test_suite/json_rpc_api/decentralized
        pytest "$testFile"
        popd
        ./reset.sh
    done

    else
        ./ready.sh
        pytest test_suite/json_rpc_api/decentralized/test_decentralization"$n".py
        if [[ ${allFlag} -eq 1 ]];then
            pushd test_suite/json_rpc_api
            pytest --ignore=decentralized --ignore=scenario
            popd
        fi
        tbears stop
        cp -rf .score/ .score2/
        cp -rf .statedb/ .statedb2/
fi

