import os
from typing import List

from iconsdk.builder.transaction_builder import TransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from .base import Base

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestPreVote(Base):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    def setUp(self):
        super().setUp()

        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

    def _distribute_icx(self, addresses: List['KeyWallet']):
        tx_list = []
        for key_wallet in addresses:
            transaction = TransactionBuilder(). \
                value(10**18). \
                from_(self._test1.get_address()). \
                to(key_wallet.get_address()). \
                nid(3). \
                nonce(1). \
                step_limit(1000000). \
                version(3). \
                build()
            signed_transaction = SignedTransaction(transaction, self._test1)
            tx_list.append(signed_transaction)
        return tx_list

    def test_1_register_one_prep_invalid_case1(self):
        account = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1, account.get_address(), 10**16)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "detail",
            "publicKey": "0x1234"
        }
        tx = self.create_register_prep_tx(account, params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

    def test_2_register_one_prep_invalid_case2(self):
        account = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1, account.get_address(), 10**16)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100"
        }
        tx = self.create_register_prep_tx(account, params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

    def test_3_register_one_prep(self):
        account = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1, account.get_address(), 10**16)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "detail",
            "publicKey": "0x1234",
            "p2pEndPoint": "target://123.213.123.123:7100"
        }
        tx = self.create_register_prep_tx(account, params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        # set prep on pre-voting
        params = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100"
        }
        tx = self.create_set_prep_tx(account, set_data=params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        # set irep on pre-voting
        irep = 40000
        params = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100",
        }
        tx = self.create_set_prep_tx(self._wallet_array[0], irep, params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

    def test_4_register_100_preps_and_check_total_delegated(self):
        accounts = [KeyWallet.create() for _ in range(100)]
        self._distribute_icx(accounts)
        tx_list = []
        for i in range(100):
            params = {
                "name": f"banana node{i}",
                "email": f"banana@banana{i}.com",
                "website": f"https://banana{i}.com",
                "details": f"detail{i}",
                "publicKey": f"0x1234",
                "p2pEndPoint": f"target://{i}.213.123.123:7100"
            }
            tx = self.create_register_prep_tx(accounts[i], params)
            tx_list.append(tx)

        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)

        for result in tx_results:
            self.assertEqual(result['status'], 1)

        # check total delegated
        # distribute icx
        delegators = [KeyWallet.create() for _ in range(10)]
        tx_list = self._distribute_icx(delegators)
        tx_result = self.process_transaction_bulk(tx_list, self.icon_service)

        # stake
        stake_tx_list = []
        for index, key_wallet in enumerate(delegators):
            tx = self.create_set_stake_tx(key_wallet, 10**18)
            stake_tx_list.append(tx)

        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)

        # delegate
        delegate_info_list = []
        delegate_amount = [100 - i for i in range(100)]
        for index, key_wallet in enumerate(accounts):
            delegate_info = (key_wallet.get_address(), 100-index)
            delegate_info_list.append(delegate_info)

        delegate_tx_list = []
        for index, key_wallet in enumerate(delegators):
            tx = self.create_set_delegation_tx(key_wallet, delegate_info_list[index*10:index*10+10])
            delegate_tx_list.append(tx)
        tx_results = self.process_transaction_bulk(delegate_tx_list, self.icon_service)

        # check total Delegated 50 to 70
        response_50_to_70 = self.get_prep_list(50, 70)
        self.assertEqual(response_50_to_70['totalDelegated'], hex(sum(delegate_amount[49:70])))
