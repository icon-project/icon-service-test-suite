
from typing import TYPE_CHECKING, List

from iconsdk.wallet.wallet import KeyWallet

from test_suite.json_rpc_api.base import Base, ICX_FACTOR

if TYPE_CHECKING:
    from iconsdk.signed_transaction import SignedTransaction


class TestStake(Base):

    def test_stake1(self):
        init_balance: int = 1000 * ICX_FACTOR
        init_block_height: int = self._get_block_height()

        # create user0 ~ 1
        account: 'KeyWallet' = KeyWallet.create()
        tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, account, init_balance)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # set stake user0 50%
        stake_value: int = 100 * ICX_FACTOR // 2
        tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
        init_balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 50%
        response: dict = self.get_stake(account)
        expected_result: dict = {
            "stake": hex(stake_value)
        }
        self.assertEqual(expected_result, response)

        # get balance
        response: dict = self.get_balance(account)
        expected_result: int = init_balance - stake_value
        self.assertEqual(expected_result, response)

        # set stake user0 100%
        stake_value: int = 100 * ICX_FACTOR
        tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
        init_balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 100%
        response: dict = self.get_stake(account)
        expected_result: dict = {
            "stake": hex(stake_value)
        }
        self.assertEqual(expected_result, response)

        # get balance
        response: dict = self.get_balance(account)
        expected_result: int = init_balance - stake_value
        self.assertEqual(expected_result, response)

        # set stake user0 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 100 * ICX_FACTOR // 2
        tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
        init_balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 50% again
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
        tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
        init_balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 100% again
        response: dict = self.get_stake(account)
        expected_result: dict = {
            "stake": hex(stake_value)
        }
        self.assertEqual(expected_result, response)

        # get balance
        response: dict = self.get_balance(account)
        expected_result: int = init_balance - stake_value
        self.assertEqual(expected_result, response)

        # set stake user0 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 100 * ICX_FACTOR // 2
        tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
        init_balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 50% again
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
        tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
        init_balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 150% again
        response: dict = self.get_stake(account)
        expected_result: dict = {
            "stake": hex(stake_value)
        }
        self.assertEqual(expected_result, response)

        # set stake user0 50% again
        prev_stake_value: int = stake_value
        stake_value: int = 50 * ICX_FACTOR // 2
        tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
        init_balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 50% again
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
        tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
        init_balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 0% again
        response: dict = self.get_stake(account)
        expected_result: dict = {
            "stake": hex(stake_value),
            "unstake": hex(prev_stake_value - stake_value),
        }
        self.assertEqual(expected_result['stake'], response['stake'])
        self.assertEqual(expected_result['unstake'], response['unstake'])
        self.assertIn('unstakeBlockHeight', response)

        prev_block: int = self._get_block_height()
        expired_block_height: int = int(response['unstakeBlockHeight'], 16) - self._get_block_height()
        self._make_blocks(prev_block + expired_block_height + 1)

        # get balance
        response: dict = self.get_balance(account)
        expected_result: int = init_balance
        self.assertEqual(expected_result, response)

    def test_stake2(self):
        init_balance: int = 1000 * ICX_FACTOR
        init_account_count: int = 100
        user_balances = [init_balance] * init_account_count
        init_block_height: int = self._get_block_height()

        # create user0 ~ 1
        tx_list: list = []
        accounts: List['KeyWallet'] = [KeyWallet.create() for _ in range(init_account_count)]
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, account, init_balance)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # set stake user0 50%
        tx_list: list = []
        stake_value: int = 100 * ICX_FACTOR // 2
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for i, tx_result in enumerate(tx_results):
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])
            user_balances[i] -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 50%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for i, account in enumerate(accounts):
            response: dict = self.get_balance(account)
            expected_result: int = user_balances[i] - stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 100%
        tx_list: list = []
        stake_value: int = 100 * ICX_FACTOR
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for i, tx_result in enumerate(tx_results):
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])
            user_balances[i] -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for i, account in enumerate(accounts):
            response: dict = self.get_balance(account)
            expected_result: int = user_balances[i] - stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 50% again
        tx_list: list = []
        prev_stake_value: int = stake_value
        stake_value: int = 100 * ICX_FACTOR // 2
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for i, tx_result in enumerate(tx_results):
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])
            user_balances[i] -= tx_result['stepUsed'] * tx_result['stepPrice']

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

        # get balance
        for i, account in enumerate(accounts):
            response: dict = self.get_balance(account)
            expected_result: int = user_balances[i] - prev_stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 100% again
        tx_list: list = []
        stake_value: int = 100 * ICX_FACTOR
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for i, tx_result in enumerate(tx_results):
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])
            user_balances[i] -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 100% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for i, account in enumerate(accounts):
            response: dict = self.get_balance(account)
            expected_result: int = user_balances[i] - stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 50% again
        tx_list: list = []
        prev_stake_value: int = stake_value
        stake_value: int = 100 * ICX_FACTOR // 2
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for i, tx_result in enumerate(tx_results):
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])
            user_balances[i] -= tx_result['stepUsed'] * tx_result['stepPrice']

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

        # get balance
        for i, account in enumerate(accounts):
            response: dict = self.get_balance(account)
            expected_result: int = user_balances[i] - prev_stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 150% again
        tx_list: list = []
        stake_value: int = 150 * ICX_FACTOR
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for i, tx_result in enumerate(tx_results):
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])
            user_balances[i] -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 150% again
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get balance
        for i, account in enumerate(accounts):
            response: dict = self.get_balance(account)
            expected_result: int = user_balances[i] - stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 50% again
        tx_list: list = []
        prev_stake_value: int = stake_value
        stake_value: int = 50 * ICX_FACTOR // 2
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for i, tx_result in enumerate(tx_results):
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])
            user_balances[i] -= tx_result['stepUsed'] * tx_result['stepPrice']

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

        # get balance
        for i, account in enumerate(accounts):
            response: dict = self.get_balance(account)
            expected_result: int = user_balances[i] - prev_stake_value
            self.assertEqual(expected_result, response)

        # set stake user0 0% again
        tx_list: list = []
        stake_value: int = 0
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for i, tx_result in enumerate(tx_results):
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])
            user_balances[i] -= tx_result['stepUsed'] * tx_result['stepPrice']

        # get stake user0 0% again
        last_unstake_block_height: str = hex(0)
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value),
                "unstake": hex(prev_stake_value - stake_value),
            }
            self.assertEqual(expected_result['stake'], response['stake'])
            self.assertEqual(expected_result['unstake'], response['unstake'])
            self.assertIn('unstakeBlockHeight', response)
            last_unstake_block_height = response['unstakeBlockHeight']

        prev_block: int = self._get_block_height()
        expired_block_height: int = int(last_unstake_block_height, 16) - self._get_block_height()
        self._make_blocks(prev_block + expired_block_height + 1)

        # get balance
        for i, account in enumerate(accounts):
            response: dict = self.get_balance(account)
            expected_result: int = user_balances[i] - stake_value
            self.assertEqual(expected_result, response)
