import unittest
from utils import W3cls, StateChannel
from StateChannelBackend import StateChannelBackend
from StateChannelFrontend import StateChannelFrontend

class TestStateChannelSol(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		pass

	@classmethod
	def tearDownClass(cls):
		pass

	def setUp(self):
		addresses = W3cls.w3.eth.accounts[:3]
		caps = [50, 50, 50]

		self.back = StateChannelBackend()

		self.fronts = {addr: StateChannelFrontend(account=addr, cap=cap) 
			for addr, cap in zip(self.addresses, caps)}

	def tearDown(self):
		pass

    def test_normal_usage(self):
    	f = self.fronts
    	b = self.back

    	r = f[0].createReceipt(allowed_funds=10, channel_number=0)
		self.assertTrue(b.receiveReceipt(r))
		
		r = f[1].createReceipt(allowed_funds=10, channel_number=0)
    	self.assertTrue(b.receiveReceipt(r))
    	r = f[1].createReceipt(allowed_funds=15, channel_number=0)
		self.assertTrue(b.receiveReceipt(r))

		r = f[2].createReceipt(allowed_funds=20, channel_number=0)
    	self.assertTrue(b.receiveReceipt(r))
		r = f[2].createReceipt(allowed_funds=15, channel_number=0)
    	self.assertTrue(b.receiveReceipt(r))

    	f[0].createReceipt(allowed_funds=10, channel_number=0)
    	f[0].createReceipt(allowed_funds=10, channel_number=0)
    	f[0].createReceipt(allowed_funds=10, channel_number=0)
    	

    # def test_normal_usage(self):

    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()
