import json
import typing

from web3 import Web3

Receipt = typing.NamedTuple("Receipt", [
    ("v", int), ("r", str), ("s", str),
    ("account", str),
    ("allowed_funds", int),
    ("channel_number", int),
    ("timestamp", float)])


class W3cls():
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    assert w3.eth.blockNumber

    @classmethod
    def normalizeAddress(cls, address):
        return cls.w3.toChecksumAddress(address)

    @staticmethod
    def ethToWei(x):
        return x * 1000000000000000000
        # return x*100

    @staticmethod
    def weiToEth(x):
        return x // 1000000000000000000
        # return x*100


class StateChannel():
    def __init__(self, contract_path="/home/jack/eth_labs/code/project/truffle/build/contracts/StateChannel.json"):
        with open(contract_path, "r") as f:
            self.contract_data = json.load(f)

        self.address = W3cls.normalizeAddress(self.contract_data["networks"]["5777"]["address"])
        self.contract = W3cls.w3.eth.contract(address=self.address, abi=self.contract_data["abi"])
        self.contract_owner = W3cls.normalizeAddress(self.contract.functions.owner().call())
        self.punishment = self.contract.functions.PUNISHMENT().call()

    def _transactContract(self, method, t_params: dict):
        t_params["gas"] = "90000"
        fs = method.transact(t_params)
        W3cls.w3.eth.waitForTransactionReceipt(fs)

    def isOpen(self, user: str, channel_number: int):
        return self.contract.functions.isChannelOpen(user, int(channel_number)).call()
