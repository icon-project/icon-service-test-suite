#!/usr/bin/env bash

tbears stop
tbears clear
tbears start

pytest test_suite/init_test.py

cp -rf .score/ .score2/
cp -rf .statedb/  .statedb2/