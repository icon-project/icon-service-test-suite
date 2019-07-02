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
        block_height: int = 0
        if self.icon_service:
            block = self.icon_service.get_block("latest")
            block_height = block['height']
        return block_height

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
                .from_(account.get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .step_limit(10_000_000) \
                .nid(3) \
                .nonce(100) \
                .method("registerPRep") \
                .params(info) \
                .build()
            signed_transaction = SignedTransaction(transaction, account)
            tx_list.append(signed_transaction)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

    def _set_stake_bulk(self, accounts: list, get_stake: callable):
        # set stake
        tx_list: list = []
        for i, account in enumerate(accounts):
            stake_value: int = get_stake(i)
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

    def _get_stake_bulk(self, accounts: list, get_stake: callable):
        for i, account in enumerate(accounts):
            stake_value: int = get_stake(i)
            call = CallBuilder().from_(account.get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getStake") \
                .params({"address": account.get_address()}) \
                .build()
            response = self.process_call(call, self.icon_service)
            expected_result = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

    def _set_delegate(self,
                      account: 'KeyWallet',
                      accounts: list,
                      cnt: int,
                      start_index: int,
                      delegation_value: int):
        delegations: list = []
        if delegation_value > 0:
            for i in range(start_index, start_index + cnt):
                delegation: dict = {
                    "address": str(accounts[i].get_address()),
                    "value": hex(delegation_value)
                }
                delegations.append(delegation)
        transaction = CallTransactionBuilder() \
            .from_(account.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("setDelegation") \
            .params({"delegations": delegations}) \
            .build()
        signed_transaction = SignedTransaction(transaction, account)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

    def _get_delegate(self,
                      account: 'KeyWallet',
                      accounts: list,
                      cnt: int,
                      start_index: int,
                      init_balance: int,
                      delegation_value: int):
        expected_delegations: list = []
        expected_total_delegation: int = delegation_value * cnt
        expected_voting_power: int = init_balance - expected_total_delegation
        if delegation_value > 0:
            for i in range(start_index, start_index + cnt):
                delegation: dict = {
                    "address": str(accounts[i].get_address()),
                    "value": hex(delegation_value)
                }
                expected_delegations.append(delegation)
        call = CallBuilder().from_(account.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .method("getDelegation") \
            .params({"address": account.get_address()}) \
            .build()
        response = self.process_call(call, self.icon_service)
        expected_result = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        self.assertEqual(expected_result, response)

    def _get_prep_list(self, account: 'KeyWallet', expected_delegated: int):
        call = CallBuilder().from_(account.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .method("getPRepList") \
            .params({}) \
            .build()

        response = self.process_call(call, self.icon_service)
        total_delegated = response["totalDelegated"]
        self.assertEqual(hex(expected_delegated), total_delegated)

    def test_delegate3(self):
        init_balance: int = 100
        init_account_count: int = 2
        init_block_height: int = self._get_block_height()

        accounts: list = []
        self._make_account_bulk(accounts, balance=init_balance, count=init_account_count)

        # register prep
        preps = [accounts[0]]
        self._init_prep(preps)

        # set stake
        self._set_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance)

        # get stake
        self._get_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance)

        # set delegate to user1 100%
        account = accounts[0]
        start_index: int = 1
        cnt: int = 1
        delegation_value: int = init_balance
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate user1 100%
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

        # set delegate to user1 50%
        account = accounts[0]
        start_index: int = 1
        cnt: int = 1
        delegation_value: int = init_balance // 2
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate user1 50%
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

        # set delegate to user1 0%
        account = accounts[0]
        start_index: int = 1
        cnt: int = 1
        delegation_value: int = 0
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate user1 0%
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

    def test_delegate4(self):
        init_balance: int = 100
        init_account_count: int = 2
        init_block_height: int = self._get_block_height()

        accounts: list = []
        self._make_account_bulk(accounts, balance=init_balance, count=init_account_count)

        # register prep
        self._init_prep(accounts)

        # set stake
        self._set_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance)

        # get stake
        self._get_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance)

        # set delegate to user1 100%
        account = accounts[0]
        start_index: int = 1
        cnt: int = 1
        delegation_value: int = init_balance
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate user1 100%
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

        self._get_prep_list(account, 0)

        # set delegate to user1 50%
        account = accounts[0]
        start_index: int = 1
        cnt: int = 1
        delegation_value: int = init_balance // 2
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate user1 50%
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

        # set delegate to user1 0%
        account = accounts[0]
        start_index: int = 1
        cnt: int = 1
        delegation_value: int = 0
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate user1 0%
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

    def test_delegate5(self):
        init_balance: int = 100
        init_account_count: int = 3
        init_block_height: int = self._get_block_height()

        accounts: list = []
        self._make_account_bulk(accounts, balance=init_balance, count=init_account_count)

        # register prep
        self._init_prep(accounts)

        # set stake
        self._set_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance)

        # get stake
        self._get_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance)

        # set delegate user0 ~ 1
        account = accounts[0]
        start_index: int = 0
        cnt: int = 2
        delegation_value: int = init_balance // cnt // 2
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate user0 ~ 1
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

        # set delegate user1 ~ 2
        account = accounts[0]
        start_index: int = 1
        cnt: int = 2
        delegation_value: int = init_balance // cnt // 2
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegation user1 ~ 2
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

    def test_delegate6(self):
        init_balance: int = 100
        init_account_count: int = 40
        init_block_height: int = self._get_block_height()

        accounts: list = []
        self._make_account_bulk(accounts, balance=init_balance, count=init_account_count)

        # register prep
        self._init_prep(accounts)

        # set stake
        self._set_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance)

        # get stake
        self._get_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance)

        # set delegate user0 ~ 9
        account = accounts[0]
        start_index: int = 0
        cnt: int = 10
        delegation_value: int = init_balance // cnt // 2
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate user0 ~ 9
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

        # set delegate user10 ~ 19
        account = accounts[0]
        start_index: int = 10
        cnt: int = 10
        delegation_value: int = init_balance // cnt // 2
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate 10 ~ 19
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

        # set over delegate 20 ~ 29 + 1 (Fail)
        account = accounts[0]
        start_index: int = 20
        cnt: int = 10 + 1
        delegations: list = []
        for i in range(start_index, start_index + cnt):
            delegation: dict = {
                "address": str(accounts[i].get_address()),
                "value": hex(delegation_value)
            }
            delegations.append(delegation)
        transaction = CallTransactionBuilder() \
            .from_(account.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("setDelegation") \
            .params({"delegations": delegations}) \
            .build()
        signed_transaction = SignedTransaction(transaction, account)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(0, tx_result['status'])

        # get delegate rollback (10 ~ 19)
        account = accounts[0]
        start_index: int = 10
        cnt: int = 10
        delegation_value: int = init_balance // cnt // 2
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

        # set delegate all users 0loop
        account = accounts[0]
        cnt = 0
        start_index = 20
        delegation_value = 0
        self._set_delegate(account, accounts, cnt, start_index, delegation_value)

        # get delegate all users 0loop
        account = accounts[0]
        cnt = 0
        start_index = 20
        delegation_value = 0
        self._get_delegate(account, accounts, cnt, start_index, init_balance, delegation_value)

    def test_delegate7(self):
        init_balance: int = 100
        init_account_count: int = 100
        init_block_height: int = self._get_block_height()

        accounts: list = []
        self._make_account_bulk(accounts, balance=init_balance, count=init_account_count)

        # register prep
        self._init_prep(accounts)

        # set stake
        self._set_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance - x % 100 // 2)

        # get stake
        self._get_stake_bulk(accounts=accounts,
                             get_stake=lambda x: init_balance - x % 100 // 2)

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

        # get delegate
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
        for i, account in enumerate(accounts):
            stake_value: int = init_balance - i % 100 // 2
            call = CallBuilder().from_(account.get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getPRep") \
                .params({"address": account.get_address()}) \
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
            signed_transaction = SignedTransaction(transaction, account)
            tx_list.append(signed_transaction)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

        # get delegate
        for i, account in enumerate(accounts):
            total_delegation_value: int = init_balance - i % 100 // 2
            call = CallBuilder().from_(account.get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getDelegation") \
                .params({"address": account.get_address()}) \
                .build()
            response = self.process_call(call, self.icon_service)
            expected_result = {
                "delegations": [],
                "totalDelegated": hex(0),
                "votingPower": hex(total_delegation_value)
            }
            self.assertEqual(expected_result, response)

        # get prep
        for i, account in enumerate(accounts):
            stake_value: int = init_balance - i % 100 // 2
            call = CallBuilder().from_(account.get_address()) \
                .to(self.SYSTEM_ADDRESS) \
                .method("getPRep") \
                .params({"address": account.get_address()}) \
                .build()
            response = self.process_call(call, self.icon_service)
            delegation = response["delegation"]
            expected_result = {
                "stake": hex(stake_value),
                "delegated": hex(0)
            }
            self.assertEqual(expected_result, delegation)
