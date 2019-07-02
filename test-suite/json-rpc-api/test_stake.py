import os
from random import randrange

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import CallTransactionBuilder, DeployTransactionBuilder, TransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.address import GOVERNANCE_SCORE_ADDRESS
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey, REV_IISS
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

GOVERNANCE_SCORES = [
    '769282ab3dee78378d7443fe6c1344c76e718734e7f581961717f12a121a2be8',
    '83537e56c647fbf0b726286ee08d31f12dba1bf7e50e8119eaffbf48004f237f'
]


class TestScoreTest(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '../'))
    SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"
    GOVERNANCE_ADDRESS = "cx0000000000000000000000000000000000000001"

    def setUp(self):
        super().setUp(block_confirm_interval=1, network_only=True)

        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # deploy governance SCORE
        for score in GOVERNANCE_SCORES:
            score_path = os.path.abspath(os.path.join(self.SCORE_PROJECT, f'./data/{score}.zip'))
            self._deploy_score(score_path=score_path, to=self.GOVERNANCE_ADDRESS)

        # set revision
        self._set_revision(REV_IISS)

        self.accounts: list = []
        init_balance: int = 100
        init_account_count: int = 101
        self._make_account_bulk(self.accounts, balance=init_balance, count=init_account_count)

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

    def _set_revision(self, revision: int):
        account = self._test1

        # Generates a 'setStake' instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(account.get_address()) \
            .to(str(GOVERNANCE_SCORE_ADDRESS)) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("setRevision") \
            .params({"code": hex(revision),
                     "name": f"1.1.{revision}"}) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, account)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

    def _deploy_score(self, score_path: str, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(score_path)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def _transfer_icx(self, from_: str, to: str, value: int):
        # Generates an instance of transaction for sending icx.
        transaction = TransactionBuilder() \
            .from_(from_) \
            .to(to) \
            .value(value) \
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

        return tx_result

    def _stake(self, account: 'KeyWallet', stake_value: int):
        # Generates a 'setStake' instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(account.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("setStake") \
            .params({"value": stake_value}) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, account)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        return tx_result

    def _get_stake(self, account: 'KeyWallet') -> dict:
        # Generates a 'getStake' call instance using the CallBuilder
        call = CallBuilder().from_(account.get_address()) \
            .to(self.SYSTEM_ADDRESS) \
            .method("getStake") \
            .params({"address": account.get_address()}) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        return response

    def _make_dummy_block(self):
        tx_result = self.process_message_tx(self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

    def test_stake_for_one_time(self):
        stake_value: int = 100
        half_of_stake_value: int = 100 // 2
        unstake_value: int = 0
        unstake_lock_period = default_icon_config[ConfigKey.IISS_UNSTAKE_LOCK_PERIOD]
        account = self.accounts[0]
        init_balance = self.icon_service.get_balance(account.get_address())

        # stake 50%
        self._stake(account, half_of_stake_value)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - balance, half_of_stake_value)
        respones_for_stake = self._get_stake(account)

        expect_result = {
            "stake": hex(half_of_stake_value)
        }

        self.assertEqual(expect_result, respones_for_stake)

        # stake 100%
        self._stake(account, stake_value)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - balance, stake_value)
        respones_for_stake = self._get_stake(account)

        expect_result = {
            "stake": hex(stake_value)
        }

        self.assertEqual(expect_result, respones_for_stake)

        # un-stake 50%
        tx_result = self._stake(account, half_of_stake_value)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - balance, stake_value)
        respones_for_stake = self._get_stake(account)

        expect_result = {
            "stake": hex(half_of_stake_value),
            "unstake": hex(half_of_stake_value),
            "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
        }

        self.assertEqual(expect_result, respones_for_stake)

        # un-stake 100%
        tx_result = self._stake(account, unstake_value)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - balance, stake_value)
        respones_for_stake = self._get_stake(account)
        expect_result = {
            "stake": hex(0),
            "unstake": hex(100),
            "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
        }
        self.assertEqual(expect_result, respones_for_stake)

        for _ in range(8):
            self._make_dummy_block()

        # un-stake 100%
        tx_result = self._stake(account, unstake_value)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - balance, stake_value)
        respones_for_stake = self._get_stake(account)
        expect_result = {
            "stake": hex(0),
            "unstake": hex(100),
            "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
        }
        self.assertEqual(expect_result, respones_for_stake)

    def test_stake_for_100_times(self):
        for i in range(1, 101):
            stake_value: int = 100
            part_of_stake_value: int = randrange(1, 100)
            unstake_value: int = stake_value - part_of_stake_value
            unstake_lock_period = default_icon_config[ConfigKey.IISS_UNSTAKE_LOCK_PERIOD]
            account = self.accounts[i]
            init_balance = self.icon_service.get_balance(account.get_address())

            # stake random
            self._stake(account, part_of_stake_value)
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(init_balance - balance, part_of_stake_value)
            respones_for_stake = self._get_stake(account)

            expect_result = {
                "stake": hex(part_of_stake_value)
            }

            self.assertEqual(expect_result, respones_for_stake)

            # stake 100%
            self._stake(account, stake_value)
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(init_balance - balance, stake_value)
            respones_for_stake = self._get_stake(account)

            expect_result = {
                "stake": hex(stake_value)
            }

            self.assertEqual(expect_result, respones_for_stake)

            # un-stake random
            tx_result = self._stake(account, part_of_stake_value)
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(init_balance - balance, stake_value)
            respones_for_stake = self._get_stake(account)

            expect_result = {
                "stake": hex(part_of_stake_value),
                "unstake": hex(unstake_value),
                "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
            }

            self.assertEqual(expect_result, respones_for_stake)

            # un-stake 100%
            tx_result = self._stake(account, 0)
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(init_balance - balance, stake_value)
            respones_for_stake = self._get_stake(account)
            expect_result = {
                "stake": hex(0),
                "unstake": hex(100),
                "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
            }
            self.assertEqual(expect_result, respones_for_stake)

            for _ in range(8):
                self._make_dummy_block()

            # un-stake 100%
            tx_result = self._stake(account, 0)
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(init_balance - balance, stake_value)
            respones_for_stake = self._get_stake(account)
            expect_result = {
                "stake": hex(0),
                "unstake": hex(100),
                "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
            }
            self.assertEqual(expect_result, respones_for_stake)
