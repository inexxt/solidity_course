import json
import typing
from typing import Optional

from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import config

Receipt = typing.NamedTuple("Receipt", [
    ("v", int), ("r", str), ("s", str),
    ("account", str),
    ("allowed_funds", int),
    ("channel_number", int),
    ("timestamp", float)])


STATUS_DICT = {0: "open", 1: "closing", 2: "closed"}


class W3cls():

    w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

    if config.RINKEBY:
        w3.middleware_stack.inject(geth_poa_middleware, layer=0)

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


def load_json(fname):
    with open(fname, "r") as f:
        return json.load(f)

class StateChannel():

    def __init__(self):

        if config.RINKEBY:
            self.contract_data = load_json(config.contract_path["rinkeby"])
            self.address = W3cls.normalizeAddress("0xaEAB0A3321aFfd19dCe9D51A7a45fc8781E3E1Bb")
            self.contract = W3cls.w3.eth.contract(address=self.address, abi=self.contract_data)
        else:
            self.contract_data = load_json(config.contract_path["local"])
            self.address = W3cls.normalizeAddress(self.contract_data["networks"]["5777"]["address"])
            self.contract = W3cls.w3.eth.contract(address=self.address, abi=self.contract_data["abi"])

        self.CONTRACT_ID = self.getContractId()
        self.contract_owner = W3cls.normalizeAddress(self.contract.functions.owner().call())
        self.punishment = self.contract.functions.PUNISHMENT().call()

    def _transactContract(self, method, t_params: dict):
        t_params["gas"] = "90000"
        fs = method.transact(t_params)
        W3cls.w3.eth.waitForTransactionReceipt(fs)

    def state(self, user: Optional[str], channel_number: int):
        user = self.account if not user else user
        return self.contract.functions.state(user, int(channel_number)).call()

    def closed_at(self, user: Optional[str], channel_number: int):
        user = self.account if not user else user
        return self.state(user, channel_number)[2]

    def cap(self, user: Optional[str], channel_number: int):
        user = self.account if not user else user
        return self.state(user, channel_number)[1]

    def funds_used(self, user: Optional[str], channel_number: int):
        user = self.account if not user else user
        return self.state(user, channel_number)[3]

    def status(self, user: Optional[str], channel_number: int):
        user = self.account if not user else user
        return self.state(user, channel_number)[0]

    def isOpen(self, user: Optional[str], channel_number: int):
        user = self.account if not user else user
        return STATUS_DICT[self.status(user, channel_number)] == "open"

    def isClosing(self, user: Optional[str], channel_number: int):
        user = self.account if not user else user
        return STATUS_DICT[self.status(user, channel_number)] == "closing"

    def isClosed(self, user: Optional[str], channel_number: int):
        user = self.account if not user else user
        return STATUS_DICT[self.status(user, channel_number)] == "closed"

    def getContractId(self):
        return self.contract.functions.CHANNEL_ID().call()