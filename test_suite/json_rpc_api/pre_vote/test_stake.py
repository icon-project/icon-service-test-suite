
from typing import TYPE_CHECKING, List

from iconservice.icon_constant import PREP_MAIN_AND_SUB_PREPS

from test_suite.json_rpc_api.base import Base, ICX_FACTOR

if TYPE_CHECKING:
    from test_suite.json_rpc_api.base import TestAccount
    from iconsdk.signed_transaction import Transaction, SignedTransaction


class TestStake(Base):

    def test_stake1(self):
        init_balance: int = 1000 * ICX_FACTOR
        account_count: int = 1
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # create user0
        self.distribute_icx(accounts, init_balance)

        # set stake user0 50%
        stake_value: int = 100 * ICX_FACTOR // 2
        self.set_stake(accounts, stake_value)

        # get stake user0 50%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for i, account in enumerate(accounts):
            response: int = self.get_balance(account)
            expected_result: int = account.balance - stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 100%
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake user0 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for i, account in enumerate(accounts):
            response: int = self.get_balance(account)
            expected_result: int = account.balance - stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 100 * ICX_FACTOR // 2
        self.set_stake(accounts, stake_value)

        # get stake user0 50% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)

        # set stake user0 100% again
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake user0 100% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for account in accounts:
            response: int = self.get_balance(account)
            expected_result: int = account.balance - stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 100 * ICX_FACTOR // 2
        self.set_stake(accounts, stake_value)

        # get stake user0 50% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)

        # set stake user0 150% again
        stake_value: int = 150 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake user0 150% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # set stake user0 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 50 * ICX_FACTOR // 2
        self.set_stake(accounts, stake_value)

        # get stake user0 50% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)

        # set stake user0 0% again
        stake_value: int = 0
        self.set_stake(accounts, stake_value)

        # get stake user0 0% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)

        # refund icx
        self.refund_icx(accounts)

    def test_stake2(self):
        init_balance: int = 1000 * ICX_FACTOR
        account_count: int = PREP_MAIN_AND_SUB_PREPS
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # create users
        self.distribute_icx(accounts, init_balance)

        # set stake users 50%
        stake_value: int = 100 * ICX_FACTOR // 2
        self.set_stake(accounts, stake_value)

        # get stake users 50%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for i, account in enumerate(accounts):
            response: int = self.get_balance(account)
            expected_result: int = account.balance - stake_value
            self.assertEqual(expected_result, response)

        # set stake users 100%
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake users 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for i, account in enumerate(accounts):
            response: int = self.get_balance(account)
            expected_result: int = account.balance - stake_value
            self.assertEqual(expected_result, response)

        # set stake users 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 100 * ICX_FACTOR // 2
        self.set_stake(accounts, stake_value)

        # get stake users 50% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)

        # set stake users 100% again
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake users 100% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for account in accounts:
            response: int = self.get_balance(account)
            expected_result: int = account.balance - stake_value
            self.assertEqual(expected_result, response)

        # set stake users 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 100 * ICX_FACTOR // 2
        self.set_stake(accounts, stake_value)

        # get stake users 50% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)

        # set stake users 150% again
        stake_value: int = 150 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake users 150% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # set stake users 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 50 * ICX_FACTOR // 2
        self.set_stake(accounts, stake_value)

        # get stake users 50% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)

        # set stake users 0% again
        stake_value: int = 0
        self.set_stake(accounts, stake_value)

        # get stake users 0% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)

        # refund icx
        self.refund_icx(accounts)

    def test_stake3(self):
        init_balance: int = 100 * ICX_FACTOR
        account_count: int = 1
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # gain 100 icx
        self.distribute_icx(accounts, init_balance)

        # estimate
        stake_value: int = init_balance
        tx: 'Transaction' = self.create_set_stake_tx_without_sign(accounts[0], stake_value)
        estimate_step: int = self.estimate_step(tx)
        step_price: int = self.get_step_price()
        estimate_fee: int = step_price * estimate_step

        # set full stake
        stake_value: int = accounts[0].balance
        tx: 'SignedTransaction' = self.create_set_stake_tx(accounts[0], stake_value)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(False, tx_result['status'])
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # set full stake - estimated_fee
        stake_value: int = accounts[0].balance - estimate_fee
        self.set_stake(accounts, stake_value)

        expected_balance: int = accounts[0].balance - stake_value
        response: int = self.get_balance(accounts[0])
        self.assertEqual(expected_balance, response)

        # refund icx
        self.refund_icx(accounts)
