# README

## Description

This is a project containing an example implementation of State channels for Ethereum network. It contains both the solidity code and a backend code in Python, which implements a simple store mechanics.

## Instruction

Change the `MAIN_PATH` in the `app/config/config.py` to the path where the repo is.


## Local
Run `ganache` or `ganache-cli` on port `8545`, `networkId=5777` and set `RINKEBY` in `config.py` to `False`.  
Example command:   
`ganache-cli --networkId 5777 --gasPrice 0 --defaultBalanceEther 1000 --accounts 100`

Then run `rm -rf build && truffle migrate --network development` in the `truffle` directory.
 
## Rinkeby
Run `geth` on port `8545` and set `RINKEBY` in `config.py` to `True`. Unlock accounts of the owner of the contract and client.    

Example command:  
`geth --rinkeby --rpc --rpcapi db,eth,net,web3,personal --unlock="ACC_SERV, ACC_CLI`  
where `ACC_SERV` is the (rinkeby) account of the owner and `ACC_CLI` is the account of the client. 

## Both
When the network client is running, run:  
 - `python server.py` (runs flask on `localhost:5000`)
 - then `python backend/daemon.py` (runs server daemon, prompting updates)
 - then `python client.py ACCOUNT` where `ACCOUNT` is the account of the client unlocked before (runs client CLI)


## Testing
To test, run `test.sh`.
