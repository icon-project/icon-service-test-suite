from typing import List, Tuple

from iconservice.icon_constant import IISS_MIN_IREP

from test_suite.json_rpc_api.base import Base, ICX_FACTOR, Account, PREP_REGISTER_COST_ICX


class TestSetIRep(Base):
    def test_set_irep(self):
        if not self.get_main_prep_list():
            return
        init_balance: int = (PREP_REGISTER_COST_ICX + 201) * ICX_FACTOR
        account_count: int = 3
        accounts: List['Account'] = self.create_accounts(account_count)

        iiss_info1 = self.get_iiss_info()
        irep = iiss_info1['variable']['irep']
        self.assertEqual(IISS_MIN_IREP, int(irep, 16))

        # create
        self.distribute_icx(accounts, init_balance)

        # register prep account0, 1
        self.register_prep(accounts[:2])

        prep0 = self.get_prep(accounts[0])
        self.assertEqual(hex(IISS_MIN_IREP), prep0['irep'])

        prep1 = self.get_prep(accounts[1])
        self.assertEqual(hex(IISS_MIN_IREP), prep1['irep'])

        # delegate 100icx to prep0, 200icx to prep1
        self.set_stake(accounts, 200 * ICX_FACTOR)
        delegate_amount_list = [100 * ICX_FACTOR * (i + 1) for i in range(account_count-1)]
        delegate_info: List[Tuple['Account', int]] = \
            [(prep, delegate_amount_list[i]) for i, prep in enumerate(accounts[:2])]
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

        # prep0 delegated : 100, prep1 delegated: 200
        # set irep prep0 : INITIAL_IREP * 1.2, prep1 : INITIALIREP * 0.8
        total_delegated_amount = sum(delegate_amount_list)
        prep0_irep = IISS_MIN_IREP * 11 // 10
        prep1_irep = IISS_MIN_IREP * 12 // 10
        tx_list = []
        tx_list.append(self.create_set_governance_variables_tx(accounts[0], prep0_irep))
        tx_list.append(self.create_set_governance_variables_tx(accounts[1], prep1_irep))
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        prep0 = self.get_prep(accounts[0])
        self.assertEqual(hex(prep0_irep), prep0['irep'])

        prep1 = self.get_prep(accounts[1])
        self.assertEqual(hex(prep1_irep), prep1['irep'])

        # make blocks
        self._make_blocks_to_end_calculation()

        # check calculated irep
        delegate_weighted_sum_irep = 100 * ICX_FACTOR * prep0_irep + 200 * ICX_FACTOR * prep1_irep
        delegate_weighted_avg_irep = delegate_weighted_sum_irep // total_delegated_amount
        iiss_info2 = self.get_iiss_info()
        irep = iiss_info2['variable']['irep']
        self.assertEqual(hex(delegate_weighted_avg_irep), irep)

        # register prep and check irep set properly
        self.register_prep(accounts[-1:])
        prep2 = self.get_prep(accounts[2])
        self.assertEqual(irep, prep2['irep'])

        # delegate 0 to all preps
        delegate_info: List[Tuple['Account', int]] = \
            [(prep, 0) for i, prep in enumerate(accounts[:2])]
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

        self.refund_icx(accounts)
