import json
from web3 import Web3
from collections import defaultdict, namedtuple


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
assert w3.eth.blockNumber


def tca(x):
    return w3.toChecksumAddress(x)


Receipt = namedtuple("Receipt", ["v", "r", "s", "account", "allowed_funds", "channel_number"])


class StateChannelBackend:
    
    def __init__(self):    
        with open("../project/build/contracts/StateChannel.json", "r") as f:
            contract_data = json.load(f)
            
        address = tca(contract_data["networks"]["5777"]["address"])
        
        self.contract = w3.eth.contract(address=address, abi=contract_data["abi"])
        self.owner = tca(self.contract.functions.owner().call())
        self.receipts = defaultdict(defaultdict)

    def accepting_new_channels(self) -> bool:
        return self.contract.functions.accepting_new_channels().call()
    
    def _transact_contract(self, method, t_params: dict):
        fs = method.transact(t_params)
        w3.eth.waitForTransactionReceipt(fs)
    
    def set_accepting_new_channels(self, val: bool):
        transact_params = {"from": self.owner}
        self._transact_contract(self.contract.functions.changeAcceptanceStatus(val), transact_params)

    def receiveReceipt(self, receipt):
        r = Receipt(**receipt)
        resp = self.contract.functions.verify_receipt(int(r.allowed_funds),
                                                      r.account, 
                                                      int(r.channel_number), 
                                                      int(r.v), r.r, r.s).call()
        if not resp:
            return False
        
        self.receipts[r.account][r.channel_number] = r
        return True


# TEST
def test():
    st = StateChannelBackend()
    st.set_accepting_new_channels(False)
    assert (st.accepting_new_channels() == False)
    st.set_accepting_new_channels(True)
    assert (st.accepting_new_channels() == True)

test()