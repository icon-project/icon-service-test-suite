from random import randrange

from iconsdk.wallet.wallet import KeyWallet
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey

from .base import Base


ICX_FACTOR = 10 ** 18


class TestStake(Base):

    def setUp(self):
        super().setUp()

        self.accounts: list = []
        init_balance: int = 100 * ICX_FACTOR
        init_account_count: int = 101
        self._make_account_bulk(self.accounts, balance=init_balance, count=init_account_count)

    def _make_account_bulk(self, accounts: list, balance: int = 1000, count: int = 100) -> None:
        tx_list: list = []
        for i in range(count):
            # create account
            account: 'KeyWallet' = KeyWallet.create()
            accounts.append(account)

            # Generates an instance of transaction for sending icx.
            signed_transaction = self.create_transfer_icx_tx(self._test1, account.get_address(), balance)
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
        # unstake_lock_period = default_icon_config[ConfigKey.IISS_UNSTAKE_LOCK_PERIOD]
        unstake_lock_period = 10
        account = self.accounts[0]
        init_balance = self.icon_service.get_balance(account.get_address())
        fee_list = []

        # stake 50%
        tx_result = self._stake(account, half_of_stake_value)
        fee1 = tx_result['stepUsed'] * tx_result['stepPrice']
        fee_list.append(fee1)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - half_of_stake_value - fee1, balance)
        respones_for_stake = self.get_stake(account)

        expect_result = {
            "stake": hex(half_of_stake_value)
        }

        self.assertEqual(expect_result, respones_for_stake)

        # stake 100%
        tx_result = self._stake(account, stake_value)
        fee2 = tx_result['stepUsed'] * tx_result['stepPrice']
        fee_list.append(fee2)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - stake_value - sum(fee_list), balance)
        respones_for_stake = self.get_stake(account)

        expect_result = {
            "stake": hex(stake_value)
        }

        self.assertEqual(expect_result, respones_for_stake)

        # un-stake 50%
        tx_result = self._stake(account, half_of_stake_value)
        fee3 = tx_result['stepUsed'] * tx_result['stepPrice']
        fee_list.append(fee3)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - stake_value - sum(fee_list), balance)
        respones_for_stake = self.get_stake(account)

        expect_result = {
            "stake": hex(half_of_stake_value),
            "unstake": hex(half_of_stake_value),
            "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
        }

        self.assertEqual(expect_result, respones_for_stake)

        # un-stake 100%
        tx_result = self._stake(account, unstake_value)
        fee4 = tx_result['stepUsed'] * tx_result['stepPrice']
        fee_list.append(fee4)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - stake_value - sum(fee_list), balance)
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
        fee5 = tx_result['stepUsed'] * tx_result['stepPrice']
        fee_list.append(fee5)
        balance = self.icon_service.get_balance(account.get_address())
        self.assertEqual(init_balance - stake_value - sum(fee_list), balance)
        respones_for_stake = self.get_stake(account)
        expect_result = {
            "stake": hex(0),
            "unstake": hex(100),
            "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
        }
        self.assertEqual(expect_result, respones_for_stake)

    def test_stake_for_100_times(self):
        stake_value: int = 100
        part_of_stake_value: int = randrange(1, 100)
        unstake_value: int = stake_value - part_of_stake_value
        # unstake_lock_period = default_icon_config[ConfigKey.IISS_UNSTAKE_LOCK_PERIOD]
        unstake_lock_period = 10
        init_balance_list = [self.icon_service.get_balance(account.get_address())
                             for account in self.accounts]
        fee_list = []

        # stake random
        stake_tx_list = [self.create_set_stake_tx(account, part_of_stake_value) for account in self.accounts]
        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)
        balance_list1 = [self.icon_service.get_balance(account.get_address()) for account in self.accounts]

        first_fee_list = []
        for index, tx_result in enumerate(tx_results):
            fee = tx_result['stepUsed'] * tx_result['stepPrice']
            first_fee_list.append(fee)
            self.assertEqual(init_balance_list[index] - part_of_stake_value - fee, balance_list1[index])

        for account in self.accounts:
            respones_for_stake = self.get_stake(account)

            expect_result = {
                "stake": hex(part_of_stake_value)
            }

            self.assertEqual(expect_result, respones_for_stake)

        # stake 100%
        stake_tx_list = [self.create_set_stake_tx(account, stake_value) for account in self.accounts]
        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)
        balance_list2 = [self.icon_service.get_balance(account.get_address()) for account in self.accounts]
        second_fee_list = []
        for index, tx_result in enumerate(tx_results):
            fee = tx_result['stepUsed'] * tx_result['stepPrice']
            second_fee_list.append(fee)
            self.assertEqual(init_balance_list[index] - stake_value - first_fee_list[index] - fee,
                             balance_list2[index])

        for account in self.accounts:
            respones_for_stake = self.get_stake(account)

            expect_result = {
                "stake": hex(stake_value)
            }

            self.assertEqual(expect_result, respones_for_stake)

        # un-stake random
        stake_tx_list = [self.create_set_stake_tx(account, part_of_stake_value) for account in self.accounts]
        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)
        balance_list3 = [self.icon_service.get_balance(account.get_address()) for account in self.accounts]
        third_fee_list = []
        for index, tx_result in enumerate(tx_results):
            fee = tx_result['stepUsed'] * tx_result['stepPrice']
            third_fee_list.append(fee)
            self.assertEqual(init_balance_list[index] - stake_value -
                             first_fee_list[index] - second_fee_list[index] - fee, balance_list3[index])

            respones_for_stake = self.get_stake(self.accounts[index])

            expect_result = {
                "stake": hex(part_of_stake_value),
                "unstake": hex(unstake_value),
                "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
            }

            self.assertEqual(expect_result, respones_for_stake)

        # un-stake 100%
        stake_tx_list = [self.create_set_stake_tx(account, 0) for account in self.accounts]
        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)
        balance_list4 = [self.icon_service.get_balance(account.get_address()) for account in self.accounts]
        fourth_fee_list = []
        for index, tx_result in enumerate(tx_results):
            fee = tx_result['stepUsed'] * tx_result['stepPrice']
            fourth_fee_list.append(fee)
            self.assertEqual(init_balance_list[index] - stake_value - first_fee_list[index] - second_fee_list[index] -
                             third_fee_list[index] - fee, balance_list4[index])

            respones_for_stake = self.get_stake(self.accounts[index])
            expect_result = {
                "stake": hex(0),
                "unstake": hex(100),
                "unstakeBlockHeight": hex(tx_result["blockHeight"] + unstake_lock_period)
            }
            self.assertEqual(expect_result, respones_for_stake)

        for _ in range(8):
            self._make_dummy_block()

        # un-stake 100%
        stake_tx_list = [self.create_set_stake_tx(account, 0) for account in self.accounts]
        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)
        balance_list5 = [self.icon_service.get_balance(account.get_address()) for account in self.accounts]

        for index, tx_result in enumerate(tx_results):
            fee = tx_result['stepUsed'] * tx_result['stepPrice']
            self.assertEqual(init_balance_list[index] - first_fee_list[index] - second_fee_list[index]
                             - third_fee_list[index] - fourth_fee_list[index] - fee, balance_list5[index])
            respones_for_stake = self.get_stake(self.accounts[index])
            expect_result = {
                "stake": hex(0),
            }
            self.assertEqual(expect_result, respones_for_stake)
