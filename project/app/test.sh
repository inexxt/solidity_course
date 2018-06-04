#!/bin/bash


ganache-cli --networkId 5777 --gasPrice 0 --accounts 100 --defaultBalanceEther 1000 &
cd ../truffle && rm -rf build && truffle migrate
cd ../app/
export PYTHONPATH=`pwd`

pytest .

pkill -f ganache-cli
