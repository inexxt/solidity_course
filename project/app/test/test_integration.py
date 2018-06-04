import unittest
from typing import List

from web3.testing import Testing

from backend.Server import Server
from frontend.Client import Client
from utils.utils import W3cls


def take_d_N(d: dict, N: int):
    return {k: v for e, (k, v) in enumerate(d.items()) if e < N}


def take_l_N(l: list, N: int):
    return [x for e, x in enumerate(l) if e < N]


class TestIntegration(unittest.TestCase):
    testing = Testing(W3cls.w3)

    def receipt_convert(self, x):
        return dict(x._asdict())

    def getBackBalance(self):
        return W3cls.w3.eth.getBalance(self.back.st.account)

    def getFrontBalance(self, x):
        return W3cls.w3.eth.getBalance(self.fronts[x].st.account)

    @classmethod
    def setUpClass(self):
        addresses = W3cls.w3.eth.accounts[10:20]

        self.starting_balance_front = [W3cls.w3.eth.getBalance(k) for k in addresses]

        self.back = Server(content_path="/home/jack/eth_labs/code/project/app/test/content-test.json")

        self.fronts = [Client(addr) for addr in addresses]

        self.waitingPeriod = self.back.st.contract.functions.WAITING_PERIOD().call()

    def setUp(self):
        self.starting_balance_back = self.getBackBalance()

    def waitWaitingPeriod(self):
        waitingPeriod = self.waitingPeriod
        for _ in range(waitingPeriod):
            # wow, this is so terrbily inefficient - but ganache doesn't support mine(num) RPC call -.-
            self.testing.mine()

    def test_normal_usage(self):
        f: List[Client] = take_l_N(self.fronts, 3)
        b: Server = self.back
        f_spent = [0] * len(f)

        w = W3cls.ethToWei

        content = b.content

        def create_buy(e, item, c=None):
            if c is None:
                c = f[e].st.createNewChannel(w(25))
            price = content[item]["price"]
            r = f[e].buy(price, channel_number=c)
            self.assertTrue(b.approveBuy(item, self.receipt_convert(r)))
            f_spent[e]+= price

        create_buy(0, "esher")
        create_buy(0, "monalisa")
        self.assertRaises(Exception, create_buy, 0, "monalisa", 1)

        create_buy(1, "space")
        create_buy(2, "space")

        f[2].st.startClosingChannel(0, f[2].st.curr_used_funds[0])
        self.waitWaitingPeriod()
        f[2].st.closeChannel(0)

        self.assertRaises(Exception, create_buy, 2, "esher", 0)

        b.st.closeChannel(f[0].st.account, 0)
        b.st.closeChannel(f[0].st.account, 1)
        b.st.closeChannel(f[1].st.account, 0)

        self.assertRaises(Exception, create_buy, 0, "esher", 0)

        self.assertAlmostEqual(self.starting_balance_back / (self.getBackBalance() - w(sum(f_spent))), 1)
        for e in range(len(f)):
            self.assertAlmostEqual(self.starting_balance_front[e] / (self.getFrontBalance(e) + w(f_spent[e])), 1)


if __name__ == '__main__':
    unittest.main()
