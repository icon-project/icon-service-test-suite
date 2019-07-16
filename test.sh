#!/usr/bin/env bash

./prevote_test.sh -c | tee preVoteResult.log
rm -rf .score2/ .statedb2/
./decentralization_test.sh -c | tee decentResult1.log
./reset.sh
tbears start
pushd test_suite/json_rpc_api
pytest --ignore=decentralized --ignore=scenario | tee -a ../../decentResult1.log
popd
rm -rf .score2/ .statedb2/
./decentralization_test.sh -c -a | tee decentResult2.log
tbears clear
rm -rf .score2/ .statedb2/
./decentralization_test.sh -c -d | tee decentResult3.log
