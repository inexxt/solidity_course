from web3 import Web3
from collections import namedtuple
import requests
import json


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
assert w3.eth.blockNumber


def tca(x):
    return w3.toChecksumAddress(x)

Receipt = namedtuple("Receipt", ["v", "r", "s", "account", "allowed_funds", "channel_number"])



class StateChannelClient():
    def __init__(self, 
                 account: str = "0xE58ea859e7DE7EaB1328A730CB397d9597F5aDC6", 
                 cap: int = 10):
        self.account = account
        self.cap = cap
        self.channels = []

        with open("../project/build/contracts/StateChannel.json", "r") as f:
            contract_data = json.load(f)
            
        address = tca(contract_data["networks"]["5777"]["address"])
        self.contract = w3.eth.contract(address=address, abi=contract_data["abi"])

        # Initialize StateChannel
        punishment = self.contract.functions.PUNISHMENT().call()

        self._transact_contract(
        	self.contract.functions.createNewChannel(cap), 
        	{"from": self.account, "value": self.cap + punishment})
        self.channels.append(len(self.channels))

    def _transact_contract(self, method, t_params: dict):
        fs = method.transact(t_params)
        w3.eth.waitForTransactionReceipt(fs)


    def create_receipt(self, allowed_funds: int, channel_number: int) -> Receipt:
        assert allowed_funds <= self.cap

        msg = w3.soliditySha3(["uint256", "uint256", "uint256"], [allowed_funds, int(self.account, 16), channel_number])
        
        signature = w3.eth.sign(self.account, msg)
        signature = signature.hex()

        r = signature[:66]
        s = '0x' + signature[66:130]
        v = '0x' + signature[130:132]
        v = int(v, 16)
        v = v if v in [27, 28] else v + 27

        # print(allowed_funds, self.account, channel_number, v, r, s)
        # raise Exception("aa")

        assert self.contract.functions.verify_receipt(allowed_funds, self.account, channel_number, v, r, s).call()
        return Receipt(v=v, r=r, s=s, account=self.account, channel_number=channel_number, allowed_funds=allowed_funds)

    def startClosingChannel(self, channel_number: int, used_funds: int):
        self._transact_contract(self.contract.startClosingByUser(channel_number, used_funds), {"from": self.account})

    def closeChannel(self, channel_number: int):
        self._transact_contract(self.contract.closeByUser(channel_number), {"from": self.account})