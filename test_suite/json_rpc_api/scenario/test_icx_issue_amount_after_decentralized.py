import os
from typing import List

from iconservice.icon_constant import PREP_MAIN_PREPS, REV_DECENTRALIZATION

from test_suite.json_rpc_api.base import Base, PREP_REGISTER_COST_ICX, ICX_FACTOR, Account

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestIcxIssueAmountAfterDecentralized(Base):
    def test_issue(self):
        if not self.get_main_prep_list():
            return
        prep_register_cost: int = (PREP_REGISTER_COST_ICX + 10) * ICX_FACTOR
        main_prep_accounts: List['Account'] = self.create_accounts(PREP_MAIN_PREPS)
        sub_prep_accounts: List['Account'] = self.create_accounts(1)
        iconist_accounts: List['Account'] = self.create_accounts(PREP_MAIN_PREPS)

        iconist: 'Account' = iconist_accounts[0]
        main_prep1: 'Account' = main_prep_accounts[1]
        main_prep2: 'Account' = main_prep_accounts[2]

        total_supply: int = self.icon_service.get_total_supply()

        iconist_stake_amount: int = total_supply * 2 // 100
        iconist_delegate_amount: int = iconist_stake_amount // 10

        self.distribute_icx(iconist_accounts, iconist_stake_amount + ICX_FACTOR)
        self.set_stake(iconist_accounts, iconist_stake_amount)

        # register main prep
        self.distribute_icx(main_prep_accounts, prep_register_cost + ICX_FACTOR)
        self.distribute_icx(sub_prep_accounts, prep_register_cost + ICX_FACTOR + iconist_stake_amount)
        self.register_prep(main_prep_accounts)
        self.register_prep(sub_prep_accounts)
        delegations = []
        for i, account in enumerate(iconist_accounts):
            delegations.append([(main_prep_accounts[i], iconist_delegate_amount)])
        self.set_delegation(iconist_accounts, delegations)

        sub_prep_delegations = [(main_prep_accounts[0], iconist_delegate_amount),
                                (sub_prep_accounts[0], iconist_delegate_amount)]
        self.set_delegation([iconist], [sub_prep_delegations])
        builtin_owner = Account(self._test1)

        # set Revision REV_IISS (decentralization)
        tx = self.create_set_revision_tx(builtin_owner, REV_DECENTRALIZATION)
        tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(main_prep_accounts))
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)

        calculate1_block_height: int = self._make_blocks_to_end_calculation()

        calculate2_block_height: int = self._make_blocks_to_end_calculation()
        response: dict = self.get_main_prep_list()
        print(response)
        for account in main_prep_accounts:
            response: dict = self.query_iscore(account)
            print(response)

