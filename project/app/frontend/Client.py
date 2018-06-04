from frontend.Connector import Connector
from frontend.StateChannelFrontend import StateChannelFrontend
from utils.utils import W3cls


class Client:
    def __init__(self,
                 address: str,
                 ):
        self.st = StateChannelFrontend(address)

    def buy(self, price, channel_number: int):
        price = W3cls.ethToWei(price) # price is in eth

        assert self.st.curr_used_funds[channel_number] + price <= self.st.cap(None, channel_number)
        r = self.st.createReceipt(self.st.curr_used_funds[channel_number] + price, channel_number)
        return r

    def getBalances(self):
        active_accounts = [e for e, _ in enumerate(self.st.channels) if self.st.isOpen(self.st.account, e)]
        return {s: W3cls.weiToEth(self.st.cap(None, s) - self.st.curr_used_funds[s]) for s in active_accounts}

    def viewDeletionProgress(self):
        current_block = W3cls.w3.eth.blockNumber
        closed_at = {}

        active_accounts = [e for e, _ in enumerate(self.st.channels) if self.st.isOpen(self.st.account, e)]
        for e, c in enumerate(self.st.channels):
            if c in active_accounts:
                state = self.st.contract.functions.state(self.st.account, c).call()
                closed_at[e] = state[2]

        return {k: v - current_block for k, v in closed_at.items()}