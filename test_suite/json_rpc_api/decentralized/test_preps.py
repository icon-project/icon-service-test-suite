from typing import List, Tuple

from test_suite.json_rpc_api.base import Base, ICX_FACTOR, Account, PREP_REGISTER_COST_ICX


class TestPRepChange(Base):
    def test_change_preps(self):
        if not self.get_main_prep_list():
            return
        init_balance: int = (PREP_REGISTER_COST_ICX + 201) * ICX_FACTOR
        account_count: int = 100
        accounts: List['Account'] = self.create_accounts(account_count)

        # create
        self.distribute_icx(accounts, init_balance)

        # register prep account0
        self.register_prep(accounts[:1])

        # delegate 1icx to prep0
        self.set_stake(accounts, 200 * ICX_FACTOR)
        delegate_info: List[Tuple['Account', int]] = [(accounts[0], ICX_FACTOR)]
        tx_list = []
        for i, delegate in enumerate(delegate_info):
            tx = self.create_set_delegation_tx(accounts[i], [delegate])
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # make blocks
        self._make_blocks_to_end_calculation()

        # check if account0 in main preps
        main_preps = self.get_main_prep_list()
        main_preps = list(map(lambda prep_info: prep_info['address'], main_preps['preps']))
        self.assertIn(accounts[0].wallet.get_address(), main_preps)

        # register prep account1-99
        self.register_prep(accounts[1:])

        # delegate n+1icx to prep n
        delegate_info: List[Tuple['Account', int]] = [(accounts[i], (i+1)*ICX_FACTOR) for i in range(account_count)]
        tx_list = []
        for i, delegate in enumerate(delegate_info):
            tx = self.create_set_delegation_tx(accounts[i], [delegate])
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # make blocks
        self._make_blocks_to_end_calculation()
        # check preps ranking
        main_preps = self.get_main_prep_list()
        main_preps = list(map(lambda prep_info: prep_info['address'], main_preps['preps']))
        for i, account in enumerate(reversed(accounts[-22:])):
            self.assertEqual(account.wallet.get_address(), main_preps[i])

        # unregister main preps 1st - 10th
        tx_list = [self.create_unregister_prep_tx(prep) for prep in reversed(accounts[-10:])]
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts[-10:]))
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results, 90):
            self.assertEqual(tx_result['status'], 1)
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']
        # make blocks
        self._make_blocks_to_end_calculation()
        # check preps ranking
        main_preps = self.get_main_prep_list()
        main_preps = list(map(lambda prep_info: prep_info['address'], main_preps['preps']))
        for i, account in enumerate(reversed(accounts[68:90])):
            self.assertEqual(account.wallet.get_address(), main_preps[i])

        self.refund_icx(accounts)
