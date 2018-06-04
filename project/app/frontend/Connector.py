import requests

from utils.utils import Receipt


class Connector:
    def __init__(self,
                 server_endpoint_buy: str = "http://127.0.0.1:5000/buy",
                 server_endpoint_watch: str = "http://127.0.0.1:5000/watch",
                 server_endpoint_catalog: str = "http://127.0.0.1:5000/catalog",
                 ):
        self.server_endpoint_catalog = server_endpoint_catalog
        self.server_endpoint_buy = server_endpoint_buy
        self.server_endpoint_watch = server_endpoint_watch

    def sendReceipt(self, r: Receipt, wid: str):
        r = {**dict(r._asdict()), "wid": wid}
        # print(r)
        resp = requests.post(self.server_endpoint_buy, data=r)
        return resp.json()["access_code"]

    def watch(self, wid: str, access_code: str):
        return requests.post(self.server_endpoint_watch, data={"wid": wid, "access_code": access_code}).json()[
            "content"]

    def downloadCatalog(self):
        return requests.get(self.server_endpoint_catalog).json()