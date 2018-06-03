from collections import defaultdict
from typing import Optional

import time

from utils.utils import StateChannel, Receipt


class StateChannelBackend(StateChannel):

    INACTIVITY_PERIOD = 30 # (60 * 60 * 24 * 30) # 30 days, in seconds

    def __init__(self):
        super().__init__()

        self.account = self.contract_owner
        self.receipts = defaultdict(defaultdict)

    def isAcceptingNewChannels(self) -> bool:
        return self.contract.functions.accepting_new_channels().call()

    def setAcceptingNewChannels(self, val: bool):
        transact_params = {"from": self.account}
        self._transactContract(self.contract.functions.changeAcceptanceStatus(val), transact_params)

    def receiveReceipt(self, r: Receipt) -> int:
        previous_rs: Receipt = self.receipts[r.account]

        # check that the user is not decreasing allowance
        if r.channel_number in self.receipts[r.account]:
            if int(previous_rs[r.channel_number].allowed_funds) > int(r.allowed_funds):
                return 0
            previous_funds = int(previous_rs[r.channel_number].allowed_funds)
        else:
            previous_funds = 0

        resp = self.contract.functions.verifyReceipt(int(r.allowed_funds),
                                                     r.account,
                                                     int(r.channel_number),
                                                     int(r.v), r.r, r.s).call()
        if not resp:
            return 0

        self.receipts[r.account][r.channel_number] = r
        return int(r.allowed_funds) - previous_funds

    def closeChannel(self,
                     user: str,
                     channel_number: int):
        receipt: Receipt = self.receipts[user][channel_number]
        self._transactContract(
            self.contract.functions.closeByOwner(user,
                                                 channel_number,
                                                 receipt.allowed_funds,
                                                 receipt.v,
                                                 receipt.r,
                                                 receipt.s),
            {"from": self.account}
        )

    def challenge(self, user: str, channel_number: int):
        receipt: Receipt = self.receipts[user][channel_number]
        self._transactContract(
            self.contract.functions.challengeByOwner(user,
                                                     channel_number,
                                                     receipt.allowed_funds,
                                                     receipt.v,
                                                     receipt.r,
                                                     receipt.s),
            {"from": self.account}
        )

    def isNotActive(self, user: str, channel_number: int):
        if user not in self.receipts or channel_number not in self.receipts[user]:
            return True

        return float(self.receipts[user][channel_number].timestamp) - time.time() > self.INACTIVITY_PERIOD