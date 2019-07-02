import os
from typing import List

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import CallTransactionBuilder, TransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice.icon_constant import REV_DECENTRALIZATION
from tbears.libs.icon_integrate_test import IconIntegrateTestBase

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestDecentralization(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"
    GOVERNANCE_ADDRESS = "cx0000000000000000000000000000000000000001"

    def setUp(self):
        super().setUp(block_confirm_interval=1, network_only=True)

        self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))
        self.total_supply = self.icon_service.get_total_supply()

    def _set_decentralization_revision(self):
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self.GOVERNANCE_ADDRESS) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("setRevision") \
            .params({"code": hex(REV_DECENTRALIZATION), "name": "1.4.1"}) \
            .build()
        signed_transaction = SignedTransaction(transaction, self._test1)
        return signed_transaction

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
            transaction = TransactionBuilder().\
                value(int(self.total_supply*0.03)).\
                from_(self._test1.get_address()).\
                to(key_wallet.get_address()).\
                nid(3).\
                nonce(1).\
                step_limit(1000000).\
                version(3).\
                build()
            signed_transaction = SignedTransaction(transaction, self._test1)
            tx_list.append(signed_transaction)
        return tx_list

    def _make_delegation_data(self, preps: List['KeyWallet']):
        delegation_value = self.total_supply * 3 // 1000
        delegations = []
        for key_wallet in preps:
            delegation_data = {
                "address": key_wallet.get_address(),
                "value": hex(delegation_value)
            }
            delegations.append(delegation_data)
        return delegations

    def test_1_decentralization(self):
        # distribute icx
        distribute_tx_requests = self._distribute_icx(self._wallet_array[:3])
        tx_results = self.process_transaction_bulk(distribute_tx_requests, self.icon_service)

        # stake
        stake_tx_list = []
        for i in range(31, 34):
            tx = self._stake(self._wallet_array[i], hex(int(self.total_supply*0.03)))
            stake_tx_list.append(tx)
        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)

        # delegate
        delegation_data1 = self._make_delegation_data(self._wallet_array[:10])
        delegation_tx1 = self._delegate(self._wallet_array[31], delegation_data1)
        delegation_data2 = self._make_delegation_data(self._wallet_array[10:20])
        delegation_tx2 = self._delegate(self._wallet_array[32], delegation_data2)
        delegation_data3 = self._make_delegation_data(self._wallet_array[20:30])
        delegation_tx3 = self._delegate(self._wallet_array[33], delegation_data3)

        tx_results = self.process_transaction_bulk([delegation_tx1, delegation_tx2, delegation_tx3], self.icon_service)

        # register prep
        reg_tx_list = []
        for i in range(30):
            params = {
                "name": f"banana node{i}",
                "email": f"banana@banana{i}.com",
                "website": f"https://banana{i}.com",
                "details": f"detail{i}",
                "publicKey": f"0x1234",
                "p2pEndPoint": f"target://{i}.213.123.123:7100"
            }
            tx = self._register_prep_tx(self._wallet_array[i], params)
            reg_tx_list.append(tx)
        tx_results = self.process_transaction_bulk(reg_tx_list, self.icon_service)

        # set revision to REV_DECENTRALIZATION
        set_revision_tx = self._set_decentralization_revision()
        tx_result = self.process_transaction(set_revision_tx, self.icon_service)

        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .method("getMainPRepList") \
            .params({"foo": "bar"}) \
            .build()
        response = self.process_call(call, self.icon_service)

    def test_2_normal_account_set_prep(self):
        params = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100",
        }
        tx = self._set_prep_tx(self._wallet_array[40], params)
        tx_result = self.process_transaction(tx, self.icon_service)
        print(tx_result)
        self.assertEqual(tx_result['status'], 0)

    def test_3_unregistered_prep_set_prep(self):
        tx = self._unregister_prep_tx(self._wallet_array[0])
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        params = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100",
        }

        tx = self._set_prep_tx(self._wallet_array[0], params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

    def test_4_top_sub_prep_upgrade(self):
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .method("getMainPRepList") \
            .params({"foo": "bar"}) \
            .build()
        response = self.process_call(call, self.icon_service)
