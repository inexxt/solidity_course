from collections import defaultdict

import requests
import sys

from frontend.StateChannelFrontend import StateChannelFrontend
from utils.utils import W3cls


class Client():
    def __init__(self,
                 address: str,
                 server_endpoint_buy: str = "http://127.0.0.1:5000/buy",
                 server_endpoint_watch: str = "http://127.0.0.1:5000/watch",
                 server_endpoint_catalog: str = "http://127.0.0.1:5000/catalog",
                 ):
        self.st = StateChannelFrontend(addresss)
        self.server_endpoint_catalog = server_endpoint_catalog
        self.server_endpoint_buy = server_endpoint_buy
        self.server_endpoint_watch = server_endpoint_watch
        self.used_funds = defaultdict(int)

    def sendReceipt(self, allowed_funds: int, channel_number: int, wid: str):
        r = {**dict(self.st.createReceipt(allowed_funds, channel_number)._asdict()), "wid": wid}
        print(r)
        resp = requests.post(self.server_endpoint_buy, data=r)
        return resp.json()

    def buy(self, catalog: dict, wid: str, channel_number: int):
        assert self.used_funds[channel_number] + catalog[wid] <= self.st.channels[channel_number]
        self.used_funds[channel_number] += W3cls.ethToWei(catalog[wid])
        resp = self.sendReceipt(self.used_funds[channel_number], channel_number, wid)
        return resp["access_code"]

    def watch(self, wid: str, access_code: str):
        return requests.post(self.server_endpoint_watch, data={"wid": wid, "access_code": access_code}).json()[
            "content"]

    def downloadCatalog(self):
        return requests.get(self.server_endpoint_catalog).json()

    def getBalances(self):
        active_accounts = [e for e, _ in enumerate(self.st.channels) if self.st.isOpen(self.st.account, e)]
        return {s: W3cls.weiToEth(self.st.channels[s] - self.used_funds[s]) for s in active_accounts}

    def createNewChannel(self, cap: int):
        self.st.createNewChannel(cap)

    def startDeletingChannel(self, channel_number: int):
        active_accounts = [e for e, _ in enumerate(self.st.channels) if self.st.isOpen(self.st.account, e)]
        if channel_number not in active_accounts:
            print("INFO: channel was not active")
            return

        self.st.startClosingChannel(channel_number, self.used_funds[channel_number])

    def viewDeletionProgress(self):
        # TODO show how much time is left for each channel that is being deleted
        return []

if __name__ == "__main__":
    addresss = sys.argv[1]

    client = Client(addresss)
    catalog = client.downloadCatalog()
    codes = {}

    while True:
        catalog = client.downloadCatalog()
        print(f"Catalog: {catalog}")
        balances = client.getBalances()
        print(f"Funds available on your accounts: {balances}")
        channel_number = input("Select one of the accounts or 'c' to create new: ")
        if channel_number == 'c':
            cap = input("Select cap for your new account: (in eth) ")
            cap = W3cls.ethToWei(int(cap))
            client.createNewChannel(cap)
            print("fChannel {len(client.st.channels)} created")
            continue
        else:
            channel_number = int(channel_number)

        wid = input("Select one position from the catalog: ")

        print(f"Choosing {wid}")
        if wid not in codes:
            if balances[channel_number] < catalog[wid]:
                print("You do not have enough money for that")
                continue

            codes[wid] = client.buy(catalog, wid, int(channel_number))

        print("Watching...")
        print(client.watch(wid, codes[wid]))
