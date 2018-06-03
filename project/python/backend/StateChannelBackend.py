import json
from collections import defaultdict, namedtuple
from utils import W3cls, StateChannel, Receipt


class StateChannelBackend(StateChannel):
    
    def __init__(self):    
        super().__init__(self)

        self.address = self.contract_owner
        self.receipts = defaultdict(defaultdict)

    def isAcceptingNewChannels(self) -> bool:
        return self.contract.functions.accepting_new_channels().call()
    
    def setAcceptingNewChannels(self, val: bool):
        transact_params = {"from": self.address}
        self._transactContract(self.contract.functions.changeAcceptanceStatus(val), transact_params)

    def receiveReceipt(self, receipt):
        r = Receipt(**receipt)
        previous_rs =  self.receipts[r.account][r.channel_number] 
        
        # check that the user is not decreasing allowance
        if previous_rs and previous_rs[-1].allowed_funds <= receipt.allowed_funds:
            return False

        resp = self.contract.functions.verifyReceipt(int(r.allowed_funds),
                                                      r.account, 
                                                      int(r.channel_number), 
                                                      int(r.v), r.r, r.s).call()
        if not resp:
            return False
        
        self.receipts[r.account][r.channel_number] = r
        return True


