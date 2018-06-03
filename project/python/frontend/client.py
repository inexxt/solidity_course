import requests
import json

from StateChannelFrontend import StateChannelFrontend

class Client():
    def __init__(self,
                 server_endpoint_buy: str = "http://127.0.0.1:5000/buy", 
                 server_endpoint_watch: str = "http://127.0.0.1:5000/watch", 
                 server_endpoint_catalog: str = "http://127.0.0.1:5000/catalog",
                 cap: int = 50
                 ):
        self.st = StateChannelFrontend(cap=cap)
        self.channel_number = self.st.channels[-1] # TODO
        self.server_endpoint_catalog = server_endpoint_catalog
        self.server_endpoint_buy = server_endpoint_buy
        self.server_endpoint_watch = server_endpoint_watch
        self.used_funds = 0
        self.cap = cap


    def sendReceipt(self, allowed_funds: int, channel_number: int, wid: str):
        r = {**dict(self.st.createReceipt(allowed_funds, channel_number)._asdict()), "wid": wid}
        print(r)
        resp = requests.post(self.server_endpoint_buy, data=r)
        # assert r.status_code == requests.codes.ok
        return resp.json()

    def buy(self, catalog: dict, wid: str):
        assert self.used_funds + catalog[wid] <= self.cap
        self.used_funds += catalog[wid]
        resp = self.sendReceipt(self.used_funds, self.channel_number, wid)
        return resp["access_code"]

    def watch(self, wid: str, access_code: str):
        return requests.post(self.server_endpoint_watch, data={"wid": wid, "access_code": access_code}).json()["content"]

    def download_catalog(self):
        return requests.get(self.server_endpoint_catalog).json()  


if __name__ == "__main__":
    client = Client()
    catalog = client.download_catalog()
    while True:
        print("Catalog: ")
        print(client.download_catalog())
        print(f"Available funds: {client.cap - client.used_funds}")
        wid = input("Select one position: ")
        # wid = "space"
        print(f"Choosing {wid}")
        code = client.buy(catalog, wid)
        print("Watching...")
        print(client.watch(wid, code))