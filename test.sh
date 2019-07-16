#!/usr/bin/env bash

./prevote_test.sh -c | tee preVoteResult.log

./decentralization_test.sh -c | tee decentResult1.log
./reset.sh
tbears start
pushd test_suite/json_rpc_api
pytest --ignore=decentralized | tee -a ../../decentResult1.log
popd

#./decentralization_test.sh -c -a | tee decentResult2.log
#tbears clear
#./decentralization_test.sh -c -d | tee decentResult3.log
