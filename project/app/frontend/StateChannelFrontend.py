from collections import defaultdict

import time

from utils.utils import Receipt, W3cls, StateChannel


class StateChannelFrontend(StateChannel):
    def __init__(self,
                 account: str):
        super().__init__()

        self.account = W3cls.normalizeAddress(account)
        # get previous channels
        channel_num = self.contract.functions.available_channel(self.account).call()

        self.channels = list(range(channel_num))
        self.curr_used_funds = defaultdict(int)

    def createNewChannel(self, cap: int) -> int:
        self._transactContract(
            self.contract.functions.createNewChannel(cap),
            {"from": self.account, "value": cap + self.punishment}
        )

        self.channels.append(None)
        return len(self.channels) - 1

    def createReceipt(self,
                      allowed_funds: int,
                      channel_number: int) -> Receipt:
        assert allowed_funds <= self.cap(None, channel_number)
        assert allowed_funds >= self.curr_used_funds[channel_number]

        msg = W3cls.w3.soliditySha3(
            ["uint256", "uint256", "uint256", "uint256"],
            [self.CONTRACT_ID, allowed_funds, int(self.account, 16), channel_number])

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

        self.curr_used_funds[channel_number] = allowed_funds

        return Receipt(
            v=v, r=r, s=s,
            account=self.account,
            channel_number=channel_number,
            allowed_funds=allowed_funds,
            timestamp=time.time())

    def startClosingChannel(self,
                            channel_number: int,
                            used_funds: int):
        used_funds = self.curr_used_funds[channel_number] if used_funds is None else used_funds

        self._transactContract(
            self.contract.functions.startClosingByUser(channel_number, used_funds),
            {"from": self.account}
        )

    def closeChannel(self, channel_number: int):
        self._transactContract(
            self.contract.functions.closeByUser(channel_number),
            {"from": self.account}
        )
