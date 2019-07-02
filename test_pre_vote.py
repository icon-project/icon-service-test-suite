import os
from typing import List

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import CallTransactionBuilder, TransactionBuilder
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
        self.delegators = [KeyWallet.create() for _ in range(10)]

    def _get_prep_list(self, start_index: int=None, end_index: int=None):
        params = {"foo": "bar"}
        if start_index is not None:
            params['startRanking'] = hex(start_index)
        if end_index is not None:
            params['endRanking'] = hex(end_index)
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .method("getPRepList") \
            .params(params) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

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

    def _stake(self, key_wallet: KeyWallet, stake_value: str):
        transaction = CallTransactionBuilder() \
            .from_(key_wallet.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("setStake") \
            .params({"value": stake_value}) \
            .build()
        signed_transaction = SignedTransaction(transaction, key_wallet)
        return signed_transaction

    def _delegate(self, key_wallet: KeyWallet, delegations: list):
        transaction = CallTransactionBuilder() \
            .from_(key_wallet.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("setDelegation") \
            .params({"delegations": delegations}) \
            .build()
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

    def test_4_register_99_preps(self):
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

    def test_6_set_irep_on_pre_vote(self):
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

    def test_7_check_total_delegated(self):
        # distribute icx
        tx_list = self._distribute_icx(self.delegators)
        tx_result = self.process_transaction_bulk(tx_list, self.icon_service)

        # stake
        stake_tx_list = []
        for index, key_wallet in enumerate(self.delegators):
            tx = self._stake(key_wallet, hex(10**18))
            stake_tx_list.append(tx)

        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)

        # delegate
        delegate_info_list = []
        delegate_amount = [100 - i for i in range(100)]
        for index, key_wallet in enumerate(self._wallet_array):
            delegate_info = {
                "address": key_wallet.get_address(),
                "value": hex(100-index)
            }
            delegate_info_list.append(delegate_info)

        delegate_tx_list = []
        for index, key_wallet in enumerate(self.delegators):
            tx = self._delegate(key_wallet, delegate_info_list[index*10:index*10+10])
            delegate_tx_list.append(tx)
        tx_results = self.process_transaction_bulk(delegate_tx_list, self.icon_service)

        # check total Delegated
        response = self._get_prep_list()
        self.assertEqual(response['totalDelegated'], hex(sum(delegate_amount)))
        # check total Delegated 50 to 70
        response_50_to_70 = self._get_prep_list(50, 70)
        self.assertEqual(response_50_to_70['totalDelegated'], hex(sum(delegate_amount[49:70])))
