import os
from typing import List

from iconservice.icon_constant import PREP_MAIN_PREPS, REV_DECENTRALIZATION

from test_suite.json_rpc_api.base import Base, PREP_REGISTER_COST_ICX, ICX_FACTOR, Account

DIR_PATH = os.path.abspath(os.path.dirname(__file__))
treausury_address = "hx1000000000000000000000000000000000000000"


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
        sub_prep23: 'Account' = sub_prep_accounts[0]

        total_supply: int = self.icon_service.get_total_supply()
        treausury_balance: int = self.get_balance(treausury_address)

        iconist_stake_amount: int = total_supply * 2 // 100
        iconist_delegate_amount: int = iconist_stake_amount // 10

        self.distribute_icx(iconist_accounts + sub_prep_accounts, iconist_stake_amount + ICX_FACTOR)
        self.set_stake(iconist_accounts + sub_prep_accounts, iconist_stake_amount)

        # register main prep
        self.distribute_icx(main_prep_accounts, prep_register_cost + ICX_FACTOR)
        self.distribute_icx(sub_prep_accounts, prep_register_cost + ICX_FACTOR)
        self.register_prep(main_prep_accounts)
        self.register_prep(sub_prep_accounts)
        delegations = []
        for i, account in enumerate(iconist_accounts):
            delegations.append([(main_prep_accounts[i], iconist_delegate_amount)])
        delegations.append([(sub_prep_accounts[0], iconist_delegate_amount)])
        self.set_delegation(iconist_accounts + sub_prep_accounts, delegations)

        # set Revision REV_IISS (decentralization)
        builtin_owner = Account(self._test1)
        tx = self.create_set_revision_tx(builtin_owner, REV_DECENTRALIZATION)
        tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(main_prep_accounts))
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)
        rrep = int(self.get_iiss_info()["variable"]["rrep"], 16)
        expected_rrep = 1_200
        self.assertEqual(expected_rrep, rrep)
        block_height_before_issue = self._get_block_height()

        total_supply_after_decentralized: int = self.icon_service.get_total_supply()
        treausury_balance_after_decentralized: int = self.get_balance(treausury_address)

        # ################################ term 0 (12 ~ 33)
        calculate1_block_height: int = self._make_blocks_to_end_calculation()
        issue_data_of_term0, calulated_issue_amount_of_term0, actual_issue_amount_of_term0 = \
            self.get_issue_info_after_decentralized(block_height_before_issue + 1, calculate1_block_height)
        treasury_balance_after_calc1: int = self.get_balance(treausury_address)
        total_supply_after_calc1: int = self.icon_service.get_total_supply()
        iconist_i_score_result_after_calc1 = int(self.query_iscore(iconist)['estimatedICX'], 16)
        main_prep1_i_score_result_after_calc1 = int(self.query_iscore(main_prep1)['estimatedICX'], 16)
        main_prep1_info_after_calc1 = self.get_prep(main_prep1)
        sub_prep1_i_score_result_after_calc1 = int(self.query_iscore(sub_prep23)['estimatedICX'], 16)
        sub_prep23_info_after_calc1 = self.get_prep(sub_prep23)
        rrep_after_calc1 = int(self.get_iiss_info()["variable"]["rrep"], 16)

        expected_iscore = 0
        expected_rrep = 1_072
        self.assertEqual(expected_iscore, iconist_i_score_result_after_calc1)
        self.assertEqual(expected_iscore, main_prep1_i_score_result_after_calc1)
        self.assertEqual(expected_iscore, sub_prep1_i_score_result_after_calc1)
        self.assertEqual(expected_rrep, rrep_after_calc1)

        sub_prep_actual_total_blocks = int(sub_prep23_info_after_calc1['totalBlocks'], 16)
        sub_prep_actual_validate_blocks = int(sub_prep23_info_after_calc1['validatedBlocks'], 16)
        self.assertEqual(0, sub_prep_actual_total_blocks)
        self.assertEqual(0, sub_prep_actual_validate_blocks)
        cumulatived_covered_fee = sum([issue_data[2] for issue_data in issue_data_of_term0])
        self.assertEqual(cumulatived_covered_fee + actual_issue_amount_of_term0, calulated_issue_amount_of_term0)
        # check the total supply and fee treasury

        # ################################ term 1 (34 ~ 55)
        calculate2_block_height: int = self._make_blocks_to_end_calculation()
        issue_data_of_term1, calulated_issue_amount_of_term1, actual_issue_amount_of_term1 = \
            self.get_issue_info_after_decentralized(calculate1_block_height + 1, calculate2_block_height)
        total_supply_after_calc2: int = self.icon_service.get_total_supply()
        treasury_balance_after_calc2: int = self.get_balance(treausury_address)
        iconist_i_score_result_after_calc2 = int(self.query_iscore(iconist)['estimatedICX'], 16)
        main_prep1_i_score_result_after_calc2 = int(self.query_iscore(main_prep1)['estimatedICX'], 16)
        main_prep1_info_after_calc2 =self.get_prep(main_prep1)
        sub_prep1_i_score_result_after_calc2 = int(self.query_iscore(sub_prep23)['estimatedICX'], 16)
        sub_prep23_info_after_calc2 = self.get_prep(sub_prep23)
        rrep_after_calc2 = int(self.get_iiss_info()["variable"]["rrep"], 16)

        # check the I-SCORE of iconist1 about term 0 (end of calc2)
        iconist_expected_iscore_from_excel = 7675334259259260000
        print(iconist_expected_iscore_from_excel, iconist_i_score_result_after_calc2)

        # check the I-SCORE of main-prep about term 0 (end of calc2)
        main_prep_expected_iscore_from_excel = 2269524959742350000
        print(main_prep_expected_iscore_from_excel, main_prep1_i_score_result_after_calc2)

        # check the I-SCORE of sub-prep about term 0 (end of calc2)
        sub_prep_expected_iscore_from_excel = 9520476502952230000
        print(sub_prep_expected_iscore_from_excel, sub_prep1_i_score_result_after_calc2)

        # ################################ term 2 (56 ~ 77)
        calculate3_block_height: int = self._make_blocks_to_end_calculation()
        issue_data_of_term2, calulated_issue_amount_of_term2, actual_issue_amount_of_term2 = \
            self.get_issue_info_after_decentralized(calculate2_block_height + 1, calculate3_block_height)
        total_supply_after_calc3: int = self.icon_service.get_total_supply()
        treasury_balance_after_calc3: int = self.get_balance(treausury_address)
        iconist_i_score_result_after_calc3 = int(self.query_iscore(iconist)['estimatedICX'], 16)
        main_prep1_i_score_result_after_calc3 = int(self.query_iscore(main_prep1)['estimatedICX'], 16)
        main_prep1_info_after_calc3 = self.get_prep(main_prep1)
        sub_prep1_i_score_result_after_calc3 = int(self.query_iscore(sub_prep23)['estimatedICX'], 16)
        sub_prep23_info_after_calc3 = self.get_prep(sub_prep23)
        rrep_after_calc3 = int(self.get_iiss_info()["variable"]["rrep"], 16)

        # check the I-SCORE of iconist1 about term 1 (end of calc3)
        expected_reward_of_iconist1 = 6558517506172839506
        print(expected_reward_of_iconist1, iconist_i_score_result_after_calc3
              - iconist_i_score_result_after_calc2)

        # check the I-SCORE of main-prep about term 1 (end of calc3)
        main_prep_expected_iscore_from_excel = 2269524959742350000
        print(main_prep_expected_iscore_from_excel, main_prep1_i_score_result_after_calc3
              - main_prep1_i_score_result_after_calc2)

        # check the I-SCORE of sub-prep about term 1 (end of calc3)
        sub_prep_expected_iscore_from_excel = 8403659749865810000
        print(sub_prep_expected_iscore_from_excel, sub_prep1_i_score_result_after_calc3
              - sub_prep1_i_score_result_after_calc2)

        # ################################ term 3 (78 ~ 99)
        calculate4_block_height: int = self._make_blocks_to_end_calculation()
        issue_data_of_term3, calulated_issue_amount_of_term3, actual_issue_amount_of_term3 = \
            self.get_issue_info_after_decentralized(calculate3_block_height + 1, calculate4_block_height)
        total_supply_after_calc4: int = self.icon_service.get_total_supply()
        treasury_balance_after_calc4: int = self.get_balance(treausury_address)
        iconist_i_score_result_after_calc4 = int(self.query_iscore(iconist)['estimatedICX'], 16)
        main_prep1_i_score_result_after_calc4 = int(self.query_iscore(main_prep1)['estimatedICX'], 16)
        main_prep1_info_after_calc4 = self.get_prep(main_prep1)
        sub_prep1_i_score_result_after_calc4 = int(self.query_iscore(sub_prep23)['estimatedICX'], 16)
        sub_prep23_info_after_calc4 = self.get_prep(sub_prep23)
        rrep_after_calc4 = int(self.get_iiss_info()["variable"]["rrep"], 16)

        # check the I-SCORE of iconist1 about term 1 (end of calc3)
        expected_reward_of_iconist1 = 6558517506172839506
        print(iconist_expected_iscore_from_excel, iconist_i_score_result_after_calc4
              - iconist_i_score_result_after_calc3)

        # check the I-SCORE of main-prep about term 1 (end of calc3)
        main_prep_expected_iscore_from_excel = 2269524959742350000
        print(main_prep_expected_iscore_from_excel, main_prep1_i_score_result_after_calc4
              - main_prep1_i_score_result_after_calc3)

        # check the I-SCORE of sub-prep about term 1 (end of calc3)
        sub_prep_expected_iscore_from_excel = 8403659749865810000
        print(sub_prep_expected_iscore_from_excel, sub_prep1_i_score_result_after_calc4
              - sub_prep1_i_score_result_after_calc3)

