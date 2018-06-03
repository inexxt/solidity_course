import unittest
from typing import List

from web3.testing import Testing

from backend.StateChannelBackend import StateChannelBackend
from frontend.StateChannelFrontend import StateChannelFrontend
from utils.utils import W3cls


def take_d_N(d: dict, N: int):
    return {k: v for e, (k, v) in enumerate(d.items()) if e < N}


def take_l_N(l: list, N: int):
    return [x for e, x in enumerate(l) if e < N]


class TestStateChannelSol(unittest.TestCase):
    testing = Testing(W3cls.w3)

    def receipt_convert(self, x):
        return dict(x._asdict())

    def getBackBalance(self):
        return W3cls.w3.eth.getBalance(self.back.account)

    def getFrontBalance(self, x):
        return W3cls.w3.eth.getBalance(self.fronts[x].account)

    @classmethod
    def setUpClass(self):
        addresses = W3cls.w3.eth.accounts[2:10]

        self.starting_balance_front = [W3cls.w3.eth.getBalance(k) for k in addresses]

        self.back = StateChannelBackend()

        self.fronts = [StateChannelFrontend(account=addr) for addr in addresses]

        self.waitingPeriod = self.back.contract.functions.WAITING_PERIOD().call()

    def setUp(self):
        self.starting_balance_back = self.getBackBalance()

    def waitWaitingPeriod(self):
        waitingPeriod = self.waitingPeriod
        for _ in range(waitingPeriod):
            # wow, this is so terrbily inefficient - but ganache doesn't support mine(num) RPC call -.-
            self.testing.mine()

    def test_normal_usage(self):
        f: List[StateChannelFrontend] = take_l_N(self.fronts, 3)
        b: StateChannelBackend = self.back

        w = W3cls.ethToWei

        f[0].createNewChannel(w(50))
        r = f[0].createReceipt(allowed_funds=w(1), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))

        f[1].createNewChannel(w(50))
        r = f[1].createReceipt(allowed_funds=w(1), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))
        r = f[1].createReceipt(allowed_funds=w(2), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))

        f[2].createNewChannel(w(50))
        r = f[2].createReceipt(allowed_funds=w(2), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))
        r = f[2].createReceipt(allowed_funds=w(3), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))

        f[2].startClosingChannel(0, f[2].past_used_funds[0])

        self.waitWaitingPeriod()

        f[2].closeChannel(0)

        f[0].createNewChannel(w(30))
        r = f[0].createReceipt(allowed_funds=w(5), channel_number=1)
        self.assertTrue(b.receiveReceipt(r))

        b.closeChannel(f[0].account, 0)
        b.closeChannel(f[0].account, 1)
        b.closeChannel(f[1].account, 0)
        pns = b.punishment

        self.assertAlmostEqual(self.starting_balance_back / (self.getBackBalance() - w(1 + 2 + 3 + 5)), 1)
        self.assertAlmostEqual(self.starting_balance_front[0] / (self.getFrontBalance(0) + w(1 + 5)), 1)
        self.assertAlmostEqual(self.starting_balance_front[1] / (self.getFrontBalance(1) + w(2)), 1)
        self.assertAlmostEqual(self.starting_balance_front[2] / (self.getFrontBalance(2) + w(3)), 1)

    def test_dispute_before_time_owner_wins(self):
        Id = 3
        f: StateChannelFrontend = self.fronts[Id]
        b: StateChannelBackend = self.back

        w = W3cls.ethToWei
        f.createNewChannel(w(50))

        r = f.createReceipt(allowed_funds=w(10), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))

        f.startClosingChannel(0, w(5))
        b.challenge(f.account, 0)

        self.assertAlmostEqual(self.starting_balance_back / (self.getBackBalance() - (w(10) + b.punishment)), 1)
        self.assertAlmostEqual(self.starting_balance_front[Id] / (self.getFrontBalance(Id) + (w(10) + b.punishment)), 1)

    def test_owner_can_close_by_himsel(self):
        Id = 7
        f: StateChannelFrontend = self.fronts[Id]
        b: StateChannelBackend = self.back

        w = W3cls.ethToWei
        f.createNewChannel(w(50))

        r = f.createReceipt(allowed_funds=w(10), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))

        b.closeChannel(f.account, 0)

    def test_owner_dispute_before_time_user_wins(self):
        Id = 4
        f: StateChannelFrontend = self.fronts[Id]
        b: StateChannelBackend = self.back

        w = W3cls.ethToWei
        f.createNewChannel(w(50))

        r = f.createReceipt(allowed_funds=w(10), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))

        f.startClosingChannel(0, w(10))

        self.assertRaises(ValueError, b.challenge, f.account, 0)

        self.waitWaitingPeriod()
        f.closeChannel(0)

        self.assertAlmostEqual(self.starting_balance_back / (self.getBackBalance() - w(10)), 1)
        self.assertAlmostEqual(self.starting_balance_front[Id] / (self.getFrontBalance(Id) + w(10)), 1)

    def test_dishonest_user_gets_away(self):
        Id = 5
        f: StateChannelFrontend = self.fronts[Id]
        b: StateChannelBackend = self.back
        w = W3cls.ethToWei
        f.createNewChannel(w(50))

        r = f.createReceipt(allowed_funds=w(10), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))

        f.startClosingChannel(0, w(5))
        self.waitWaitingPeriod()
        f.closeChannel(0)

        self.assertAlmostEqual(self.starting_balance_back / (self.getBackBalance() - w(5)), 1)
        self.assertAlmostEqual(self.starting_balance_front[Id] / (self.getFrontBalance(Id) + w(5)), 1)

    def test_create_and_close_multiple_channels(self):
        Id = 6
        f: StateChannelFrontend = self.fronts[Id]
        b: StateChannelBackend = self.back
        w = W3cls.ethToWei
        f.createNewChannel(w(50))

        r = f.createReceipt(allowed_funds=w(10), channel_number=0)
        self.assertTrue(b.receiveReceipt(r))
        f.startClosingChannel(0, w(10))

        f.createNewChannel(w(10))
        r = f.createReceipt(allowed_funds=w(5), channel_number=1)
        self.assertTrue(b.receiveReceipt(r))
        f.startClosingChannel(1, w(5))

        f.createNewChannel(w(10))
        r = f.createReceipt(allowed_funds=w(3), channel_number=2)
        self.assertTrue(b.receiveReceipt(r))
        f.startClosingChannel(2, w(3))

        self.waitWaitingPeriod()

        f.closeChannel(0)
        f.closeChannel(1)
        f.closeChannel(2)

        self.assertAlmostEqual(self.starting_balance_back / (self.getBackBalance() - w(10 + 5 + 3)), 1)
        self.assertAlmostEqual(self.starting_balance_front[Id] / (self.getFrontBalance(Id) + w(10 + 5 + 3)), 1)


if __name__ == '__main__':
    unittest.main()
