from collections import namedtuple
from web3 import Web3

Receipt = namedtuple("Receipt", [
	"v", "r", "s", 
	"account", 
	"allowed_funds", 
	"channel_number"])


class W3cls:
	w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
	assert w3.eth.blockNumber

	@staticmethod
	def normalizeAddress(address):
    	return W3cls.toChecksumAddress(address)


class StateChannel:
	def __init__(self, contract_path="../../truffle/build/contracts/StateChannel.json")
        with open(contract_path, "r") as f:
            self.contract_data = json.load(f)
            
        self.address = W3cls.normalizeAddress(contract_data["networks"]["5777"]["address"])
        self.contract = W3cls.w3.eth.contract(address=self.address, abi=self.contract_data["abi"])
        self.contract_owner = W3cls.normalizeAddress(self.contract.functions.owner().call())

    def _transactContract(self, method, t_params: dict):
        fs = method.transact(t_params)
        W3cls.w3.eth.waitForTransactionReceipt(fs)