import os

from iconsdk.builder.transaction_builder import CallTransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from tbears.libs.icon_integrate_test import IconIntegrateTestBase

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestPreVote(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"
    GOVERNANCE_ADDRESS = "cx0000000000000000000000000000000000000001"

    def setUp(self):
        super().setUp(block_confirm_interval=1, network_only=True)

        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

    def _register_prep_tx(self, key_wallet: 'KeyWallet', reg_data: dict):
        transaction = CallTransactionBuilder().\
            from_(key_wallet.get_address()).\
            to(self.SYSTEM_ADDRESS).\
            value(0).\
            step_limit(1000000).\
            nid(3).\
            nonce(1).\
            method("registerPRep").\
            params(reg_data).\
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

        return signed_transaction

    def _unregister_prep_tx(self, key_wallet: 'KeyWallet'):
        transaction = CallTransactionBuilder(). \
            from_(key_wallet.get_address()). \
            to(self.SYSTEM_ADDRESS). \
            value(0). \
            step_limit(1000000). \
            nid(3). \
            nonce(1). \
            method("unregitserPRep"). \
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

        return signed_transaction

    def _set_prep_tx(self, key_wallet: 'KeyWallet', set_data: dict):
        transaction = CallTransactionBuilder(). \
            from_(key_wallet.get_address()). \
            to(self.SYSTEM_ADDRESS). \
            value(0). \
            step_limit(1000000). \
            nid(3). \
            nonce(1). \
            method("setPRep"). \
            params(set_data). \
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

        return signed_transaction

    def test_1_register_one_prep_invalid_case1(self):
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "detail",
            "publicKey": "0x1234"
        }
        tx = self._register_prep_tx(self._wallet_array[0], params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

    def test_2_register_one_prep_invalid_case2(self):
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100"
        }
        tx = self._register_prep_tx(self._wallet_array[0], params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

    def test_3_register_one_prep(self):
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "detail",
            "publicKey": "0x1234",
            "p2pEndPoint": "target://123.213.123.123:7100"
        }
        tx = self._register_prep_tx(self._wallet_array[0], params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

    def test_4_register_100_preps(self):
        tx_list = []
        for i in range(1, 100):
            params = {
                "name": f"banana node{i}",
                "email": f"banana@banana{i}.com",
                "website": f"https://banana{i}.com",
                "details": f"detail{i}",
                "publicKey": f"0x1234",
                "p2pEndPoint": f"target://{i}.213.123.123:7100"
            }
            tx = self._register_prep_tx(self._wallet_array[i], params)
            tx_list.append(tx)

        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)

        for result in tx_results:
            self.assertEqual(result['status'], 1)

    def test_5_set_prep_on_pre_vote(self):
        params = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100"
        }
        tx = self._set_prep_tx(self._wallet_array[0], params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

    def test_set_irep_on_pre_vote(self):
        params = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100",
            "irep": hex(40000)
        }
        tx = self._set_prep_tx(self._wallet_array[0], params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)
