from typing import List

from iconservice.icon_constant import Revision, PREP_MAIN_PREPS

from test_suite.json_rpc_api.base import Base, PREP_REGISTER_COST_ICX, ICX_FACTOR, Account


class TestDecentralization(Base):
    def test_func(self):
        builtin_owner = Account(self._test1)
        prep_register_cost: int = (PREP_REGISTER_COST_ICX + 10) * ICX_FACTOR
        account_count: int = PREP_MAIN_PREPS * 2
        accounts: List['Account'] = self.create_accounts(account_count)
        main_preps: List['Account'] = accounts[:PREP_MAIN_PREPS]
        iconists: List['Account'] = accounts[PREP_MAIN_PREPS:]
        total_supply: int = self.icon_service.get_total_supply()

        # Minimum_delegate_amount is 0.02 * total_supply
        minimum_delegate_amount_for_decentralization: int = total_supply * 2 // 1000
        init_balance: int = minimum_delegate_amount_for_decentralization + ICX_FACTOR

        # distribute icx PREP_MAIN_PREPS ~ PREP_MAIN_PREPS + PREP_MAIN_PREPS - 1
        self.distribute_icx(iconists, init_balance)

        # stake PREP_MAIN_PREPS ~ PREP_MAIN_PREPS + PREP_MAIN_PREPS - 1
        self.set_stake(iconists, minimum_delegate_amount_for_decentralization)

        # distribute 2010icx 0 ~ PREP_MAIN_PREPS - 1
        self.distribute_icx(main_preps, prep_register_cost)
        # register PRep
        self.register_prep(main_preps)

        # delegate to PRep
        delegations = []
        for i, account in enumerate(iconists):
            delegations.append([(main_preps[i], minimum_delegate_amount_for_decentralization)])
        self.set_delegation(iconists, delegations)

        # get main prep
        response: dict = self.get_main_prep_list()
        expected_response: dict = {
            "preps": [],
            "totalDelegated": hex(0)
        }
        self.assertEqual(expected_response, response)

        # set Revision REV_IISS (decentralization)
        tx = self.create_set_revision_tx(builtin_owner, Revision.DECENTRALIZATION.value)
        tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)

        self._make_blocks_to_end_calculation()

        # get main prep
        response: dict = self.get_main_prep_list()
        expected_preps: list = []
        expected_total_delegated: int = 0
        for prep in main_preps:
            expected_preps.append({
                'address': prep.wallet.get_address(),
                'delegated': hex(minimum_delegate_amount_for_decentralization)
            })
            expected_total_delegated += minimum_delegate_amount_for_decentralization
        expected_response: dict = {
            "preps": expected_preps,
            "totalDelegated": hex(expected_total_delegated)
        }
        self.assertEqual(expected_response, response)

        self.refund_icx(accounts)
