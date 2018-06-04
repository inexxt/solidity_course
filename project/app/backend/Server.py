import json
import logging
import os
from collections import defaultdict
from typing import Optional

from utils.utils import Receipt, W3cls

from backend.StateChannelBackend import StateChannelBackend


class Server():
    def __init__(self, content_path="/home/jack/eth_labs/code/project/app/backend/content/content.json",
                       content_files_path="/home/jack/eth_labs/code/project/app/backend/content/"):
        with open(content_path, "r") as f:
            self.content = json.load(f)
        self.content_files_path = content_files_path

        self.st = StateChannelBackend()
        self.users = defaultdict(lambda: defaultdict(int))  # a mapping user -> credit

    def approveBuy(self, wid: str, receipt: dict) -> Optional[dict]:
        r = Receipt(**receipt)

        if wid not in self.content:
            return None

        if not self.st.isOpen(r.account, r.channel_number):
            return None

        self.users[r.account][r.channel_number] += self.st.receiveReceipt(r)
        if self.users[r.account][r.channel_number] >= W3cls.ethToWei(self.content[wid]["price"]):
            self.users[r.account][r.channel_number] -= W3cls.ethToWei(self.content[wid]["price"])
            return {"wid": wid, "access_code": self.content[wid]["access_code"]}
        else:
            return None

    def showContent(self, wid, acces_code):
        if wid not in self.content or self.content[wid]["access_code"] != acces_code:
            return None

        fname = self.content[wid]["file"]
        with open(os.path.join(self.content_files_path, fname), "r") as f:
            content = f.readlines()

        return {"content": "\n".join(content)}

    def closeUserAccount(self, user, channel_number):
        self.st.closeChannel(user, channel_number)
        self.users[user][channel_number] = 0

    def performMaintenanceUserAccounts(self):
        for u in self.users.keys():
            for c in self.users[u].keys():
                # app.logger.info(u, c)
                if self.st.isNotActive(u, c):
                    self.closeUserAccount(u, c)

