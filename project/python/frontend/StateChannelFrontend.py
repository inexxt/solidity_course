from collections import namedtuple
import requests
import json
from utils import Receipt, W3cls, StateChannel


class StateChannelFrontend(StateChannel):
    def __init__(self, 
                 account: str = "0xE58ea859e7DE7EaB1328A730CB397d9597F5aDC6", 
                 cap: int = 10):
        super().__init__(self)

        self.account = account
        self.cap = cap
        self.channels = []

        # Initialize StateChannel
        punishment = self.contract.functions.PUNISHMENT().call()
        self.createNewChannel(self.cap)


    def createNewChannel(self, cap: int) -> int:
        self._transactContract(
            self.contract.functions.createNewChannel(cap), 
            {"from": self.account, "value": self.cap + punishment}
        )

        self.channels.append(len(self.channels))
        return len(self.channels) - 1

    def createReceipt(self, 
                       allowed_funds: int, 
                       channel_number: int) -> Receipt:
        assert allowed_funds <= self.cap

        msg = W3cls.w3.soliditySha3(
            ["uint256", "uint256", "uint256"], 
            [allowed_funds, int(self.account, 16), channel_number])
        
        signature = W3cls.w3.eth.sign(self.account, msg)
        signature = signature.hex()

        r = signature[:66]
        s = '0x' + signature[66:130]
        v = '0x' + signature[130:132]
        v = int(v, 16)
        v = v if v in [27, 28] else v + 27

        assert self.contract.functions.verifyReceipt(
            allowed_funds, 
            self.account, 
            channel_number, 
            v, r, s).call()

        return Receipt(
            v=v, r=r, s=s, 
            account=self.account, 
            channel_number=channel_number, 
            allowed_funds=allowed_funds)

    def startClosingChannel(self, 
                            channel_number: int, 
                            used_funds: int):
        self._transact_contract(
            self.contract.startClosingByUser(channel_number, used_funds), 
            {"from": self.account}
        )

    def closeChannel(self, channel_number: int):
        self._transact_contract(
            self.contract.closeByUser(channel_number), 
            {"from": self.account}
        )