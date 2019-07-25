import os
from typing import List

from iconservice.icon_constant import PREP_MAIN_PREPS

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

        iconist_stake_amount: int = total_supply * 1 // 100
        iconist_delegate_amount: int = iconist_stake_amount // 10

        self.distribute_icx(iconist_accounts, iconist_stake_amount + ICX_FACTOR)
        self.set_stake(iconist_accounts, iconist_stake_amount)

        # register main prep
        self.distribute_icx(main_prep_accounts, prep_register_cost + ICX_FACTOR)
        self.distribute_icx(sub_prep_accounts, prep_register_cost + ICX_FACTOR + iconist_stake_amount)
        self.register_prep(main_prep_accounts)
        self.register_prep(sub_prep_accounts)

        # 모든 main prep에 0.1% 씩 delegate
        delegations = []
        for i, account in enumerate(iconist_accounts):
            delegations.append([(main_prep_accounts[i], iconist_delegate_amount)])
        self.set_delegation(iconist_accounts, delegations)

        sub_prep_delegations = [(sub_prep_accounts[0], iconist_delegate_amount // 2)]
        self.set_delegation([iconist], sub_prep_delegations)

        # prep23는 자기 자신에게 0.01 delegate
        response: dict = self.get_main_prep_list()
        expected_preps: list = []
        expected_total_delegated: int = 0

        calculate1_block_height: int = self._make_blocks_to_end_calculation()

        calculate2_block_height: int = self._make_blocks_to_end_calculation()
        response: dict = self.get_main_prep_list()
        print(response)
        for account in main_prep_accounts:
            response: dict = self.query_iscore(account)
            print(response)

