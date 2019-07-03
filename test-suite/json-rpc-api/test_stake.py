import os
from random import randrange

from iconsdk.builder.transaction_builder import TransactionBuilder
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey, REV_IISS

from .base import Base, SCORE_PROJECT, GOVERNANCE_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

GOVERNANCE_SCORES = [
    '769282ab3dee78378d7443fe6c1344c76e718734e7f581961717f12a121a2be8',
    '83537e56c647fbf0b726286ee08d31f12dba1bf7e50e8119eaffbf48004f237f'
]


class TestScoreTest(Base):

    def setUp(self):
        super().setUp()

        # deploy governance SCORE
        for score in GOVERNANCE_SCORES:
            score_path = os.path.abspath(os.path.join(SCORE_PROJECT, f'./data/{score}.zip'))
            self.create_deploy_score_tx(score_path, self._test1, GOVERNANCE_ADDRESS)

        # set revision
        self.create_set_revision_tx(self._test1, REV_IISS)

        self.accounts: list = []
        init_balance: int = 100
        init_account_count: int = 101
        self._make_account_bulk(self.accounts, balance=init_balance, count=init_account_count)

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

    def _stake(self, account: 'KeyWallet', stake_value: int):

        # Returns the signed transaction object having a signature
        signed_transaction = self.create_set_stake_tx(account, stake_value)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        return tx_result

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
        respones_for_stake = self.get_stake(account)

        expect_result = {
            "stake": hex(half_of_stake_value)
        }

        self.assertEqual(expect_result, respones_for_stake)

        # stake 100%
        self._stake(account, stake_value)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - balance, stake_value)
        respones_for_stake = self.get_stake(account)

        expect_result = {
            "stake": hex(stake_value)
        }

        self.assertEqual(expect_result, respones_for_stake)

        # un-stake 50%
        tx_result = self._stake(account, half_of_stake_value)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - balance, stake_value)
        respones_for_stake = self.get_stake(account)

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
        respones_for_stake = self.get_stake(account)
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
        respones_for_stake = self.get_stake(account)
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
            respones_for_stake = self.get_stake(account)

            expect_result = {
                "stake": hex(part_of_stake_value)
            }

            self.assertEqual(expect_result, respones_for_stake)

            # stake 100%
            self._stake(account, stake_value)
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(init_balance - balance, stake_value)
            respones_for_stake = self.get_stake(account)

            expect_result = {
                "stake": hex(stake_value)
            }

            self.assertEqual(expect_result, respones_for_stake)

            # un-stake random
            tx_result = self._stake(account, part_of_stake_value)
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(init_balance - balance, stake_value)
            respones_for_stake = self.get_stake(account)

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
            respones_for_stake = self.get_stake(account)
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
            respones_for_stake = self.get_stake(account)
            expect_result = {
                "stake": hex(0),
                "unstake": hex(100),
                "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
            }
            self.assertEqual(expect_result, respones_for_stake)
