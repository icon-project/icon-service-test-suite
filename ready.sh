#!/usr/bin/env bash

tbears stop
tbears clear
tbears start

pytest test_suite/init_test.py

cp -r .score/ .score2/
cp -r .statedb/  .statedb2/