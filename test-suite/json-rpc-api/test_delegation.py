import os

from iconsdk.builder.transaction_builder import CallTransactionBuilder, TransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from tbears.libs.icon_integrate_test import IconIntegrateTestBase

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestDelegation(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))
    SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"

    def setUp(self):
        super().setUp(block_confirm_interval=1, network_only=True)

        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

    def _make_account(self, balance: int = 1000) -> 'KeyWallet':
        # create account
        account: 'KeyWallet' = KeyWallet.create()

        # Generates an instance of transaction for sending icx.
        transaction = TransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(account.get_address()) \
            .value(balance) \
            .step_limit(1000000) \
            .nid(3) \
            .nonce(100) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        return account

    def _make_account_bulk(self, accounts: list, balance: int = 1000, count: int = 100) -> None:

        tx_list: list = []
        tx_results: list = []
        for i in range(count):
            # create account
            account: 'KeyWallet' = KeyWallet.create()
            accounts.append(account)

            # Generates an instance of transaction for sending icx.
            transaction = TransactionBuilder() \
                .from_(self._test1.get_address()) \
                .to(account.get_address()) \
                .value(balance) \
                .step_limit(1000000) \
                .nid(3) \
                .nonce(100) \
                .build()

            # Returns the signed transaction object having a signature
            signed_transaction = SignedTransaction(transaction, self._test1)
            tx_list.append(signed_transaction)

        # process the transaction
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)

        for tx in tx_results:
            self.assertTrue('status' in tx)
            self.assertEqual(1, tx['status'])

    def _get_block_height(self) -> int:
        block = self.icon_service.get_block("latest")
        return block['height']

    def _init_prep(self, accounts: list):
        tx_list: list = []
        for i, account in enumerate(accounts):
            info: dict = {
                "name": f"node{i}",
                "email": f"node{i}@example.com",
                "website": f"https://node{i}.example.com",
                "details": f"https://node{i}.example.com/details",
                "p2pEndPoint": f"https://node{i}.example.com:7100",
                "publicKey": f"0x{b'00'.hex()}"
            }

            transaction = CallTransactionBuilder() \
                .from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .step_limit(10_000_000) \
                .nid(3) \
                .nonce(100) \
                .method("registerPRep") \
                .params(info) \
                .build()
            signed_transaction = SignedTransaction(transaction, accounts[i])
            tx_list.append(signed_transaction)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

    def test_delegation6(self):
        init_balance: int = 100
        init_account_count: int = 100
        init_block_height: int = self._get_block_height()

        accounts: list = []
        self._make_account_bulk(accounts, balance=init_balance, count=init_account_count)

        # register prep
        self._init_prep(accounts)

    def test_delegation7(self):
        init_balance: int = 100
        init_account_count: int = 100
        init_block_height: int = self._get_block_height()

        accounts: list = []
        self._make_account_bulk(accounts, balance=init_balance, count=init_account_count)

        # register prep
        self._init_prep(accounts)

        # set stake
        tx_list: list = []
        for i, account in enumerate(accounts):
            stake_value: int = init_balance - i % 100 // 2
            transaction = CallTransactionBuilder() \
                .from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .step_limit(10_000_000) \
                .nid(3) \
                .nonce(100) \
                .method("setStake") \
                .params({"value": stake_value}) \
                .build()
            signed_transaction = SignedTransaction(transaction, accounts[i])
            tx_list.append(signed_transaction)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

        # get stake
        for i in range(init_account_count):
            stake_value: int = init_balance - i % 100 // 2
            call = CallBuilder().from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getStake") \
                .params({"address": accounts[i].get_address()}) \
                .build()
            response = self.process_call(call, self.icon_service)
            expected_result = {
                "stake": hex(stake_value),
                "unstake": "0x0",
                "unstakedBlockHeight": "0x0"
            }
            self.assertEqual(expected_result, response)

        # set delegate
        expected_delegation_values: dict = {}
        tx_list: list = []
        for i, account in enumerate(accounts):
            expected_delegation_values[i] = 0

            total_delegation_value: int = init_balance - i % 100 // 2
            cnt: int = i % 10
            delegations: list = []
            for j in range(cnt):
                delegation_value: int = total_delegation_value // cnt
                expected_delegation_values[j] += delegation_value
                delegation: dict = {
                    "address": str(accounts[j].get_address()),
                    "value": hex(delegation_value)
                }
                delegations.append(delegation)
            transaction = CallTransactionBuilder() \
                .from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .step_limit(10_000_000) \
                .nid(3) \
                .nonce(100) \
                .method("setDelegation") \
                .params({"delegations": delegations}) \
                .build()
            signed_transaction = SignedTransaction(transaction, accounts[i])
            tx_list.append(signed_transaction)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

        # get delegation
        for i in range(init_account_count):
            total_delegation_value: int = init_balance - i % 100 // 2
            cnt: int = i % 10
            expected_delegation: list = []
            expected_total_delegation_value: int = 0
            for j in range(cnt):
                delegation_value: int = total_delegation_value // cnt
                expected_total_delegation_value += delegation_value
                delegation: dict = {
                    "address": str(accounts[j].get_address()),
                    "value": hex(delegation_value)
                }
                expected_delegation.append(delegation)
            expected_voting_power: int = total_delegation_value - expected_total_delegation_value
            call = CallBuilder().from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getDelegation") \
                .params({"address": accounts[i].get_address()}) \
                .build()
            response = self.process_call(call, self.icon_service)
            expected_result = {
                "delegations": expected_delegation,
                "totalDelegated": hex(expected_total_delegation_value),
                "votingPower": hex(expected_voting_power)
            }
            self.assertEqual(expected_result, response)

        # get prep
        for i in range(init_account_count):
            stake_value: int = init_balance - i % 100 // 2
            call = CallBuilder().from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getPRep") \
                .params({"address": accounts[i].get_address()}) \
                .build()
            response = self.process_call(call, self.icon_service)
            delegation = response["delegation"]
            expected_result = {
                "stake": hex(stake_value),
                "delegated": hex(expected_delegation_values[i])
            }
            self.assertEqual(expected_result, delegation)

        # set delegate 0
        tx_list: list = []
        for i, account in enumerate(accounts):
            delegations: list = []
            transaction = CallTransactionBuilder() \
                .from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .step_limit(10_000_000) \
                .nid(3) \
                .nonce(100) \
                .method("setDelegation") \
                .params({"delegations": delegations}) \
                .build()
            signed_transaction = SignedTransaction(transaction, accounts[i])
            tx_list.append(signed_transaction)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

        # get delegation
        for i in range(init_account_count):
            total_delegation_value: int = init_balance - i % 100 // 2
            call = CallBuilder().from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getDelegation") \
                .params({"address": accounts[i].get_address()}) \
                .build()
            response = self.process_call(call, self.icon_service)
            expected_result = {
                "delegations": [],
                "totalDelegated": hex(0),
                "votingPower": hex(total_delegation_value)
            }
            self.assertEqual(expected_result, response)

        # get prep
        for i in range(init_account_count):
            stake_value: int = init_balance - i % 100 // 2
            call = CallBuilder().from_(accounts[i].get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getPRep") \
                .params({"address": accounts[i].get_address()}) \
                .build()
            response = self.process_call(call, self.icon_service)
            delegation = response["delegation"]
            expected_result = {
                "stake": hex(stake_value),
                "delegated": hex(0)
            }
            self.assertEqual(expected_result, delegation)