#!/bin/bash


ganache-cli --networkId 5777 --gasPrice 0 &
cd ../truffle && rm -rf build && truffle migrate
cd ../python/

pytest .

pkill -f ganache-cli
