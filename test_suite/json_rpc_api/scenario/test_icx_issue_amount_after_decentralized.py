import os
from functools import reduce
from typing import List

from iconservice.icon_constant import PREP_MAIN_PREPS, REV_DECENTRALIZATION

from test_suite.json_rpc_api.base import Base, PREP_REGISTER_COST_ICX, ICX_FACTOR, Account

DIR_PATH = os.path.abspath(os.path.dirname(__file__))
treausury_address = "hx1000000000000000000000000000000000000000"


class TestIcxIssueAmountAfterDecentralized(Base):
    def test_issue(self):
        if not self.get_main_prep_list():
            return

        # ################################ term 0 (3 ~ 25)
        # in the term 0, only delegate reward (beta3) is provided
        term0_info: dict = self.get_iiss_info()
        print(f"###################################################################################################")
        print(
            f"Term 0 START - start BH: {self._get_block_height()}, end BH: {int(term0_info['nextCalculation'], 16) - 1}")
        print(f"IISS START - start BH: {self._get_block_height()}")
        term0_rrep = int(term0_info["variable"]["rrep"], 16)
        term0_irep = int(term0_info["variable"]["irep"], 16)
        expected_rrep = 1_200
        expected_irep = 0
        self.assertEqual(expected_rrep, term0_rrep)
        self.assertEqual(expected_irep, term0_irep)

        prep_register_cost: int = (PREP_REGISTER_COST_ICX + 10) * ICX_FACTOR
        main_prep_accounts: List['Account'] = self.create_accounts(PREP_MAIN_PREPS)
        sub_prep_accounts: List['Account'] = self.create_accounts(1)
        iconist_accounts: List['Account'] = self.create_accounts(PREP_MAIN_PREPS)

        iconist: 'Account' = iconist_accounts[0]
        main_prep1: 'Account' = main_prep_accounts[1]
        sub_prep23: 'Account' = sub_prep_accounts[0]
        print(f"iconist:", iconist.wallet.get_address())
        print(f"main_prep1:", main_prep1.wallet.get_address())
        print(f"sub_prep23:", sub_prep23.wallet.get_address())

        term0_total_supply: int = self.icon_service.get_total_supply()
        term0_treausury_balance: int = self.get_balance(treausury_address)

        iconist_stake_amount: int = term0_total_supply * 2 // 100
        iconist_delegate_amount: int = iconist_stake_amount // 10
        print(f'Delegating amount per prep: {iconist_delegate_amount}')
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
        print(f"IISS Delegation Start BH: {self._get_block_height()}")

        # set Revision REV_IISS (decentralization)
        builtin_owner = self.load_admin()
        tx = self.create_set_revision_tx(builtin_owner, REV_DECENTRALIZATION)
        tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(main_prep_accounts))
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)
        print(f'set Decentralization revision at BH: {self._get_block_height()}')

        self._make_blocks_to_end_calculation()
        print(f'Term 0 End - end BH: {self._get_block_height()}')
        treasury_balance_end_term_0: int = self.get_balance(treausury_address)
        total_supply_end_term_0: int = self.icon_service.get_total_supply()
        iconist_i_score_result_end_term_0 = int(self.query_iscore(iconist)['estimatedICX'], 16)
        main_prep1_i_score_result_end_term_0 = int(self.query_iscore(main_prep1)['estimatedICX'], 16)
        main_prep1_info_end_term_0 = self.get_prep(main_prep1)
        sub_prep1_i_score_result_end_term_0 = int(self.query_iscore(sub_prep23)['estimatedICX'], 16)
        sub_prep23_info_end_term_0 = self.get_prep(sub_prep23)

        expected_iscore = 0
        self.assertEqual(expected_iscore, iconist_i_score_result_end_term_0)
        self.assertEqual(expected_iscore, main_prep1_i_score_result_end_term_0)
        self.assertEqual(expected_iscore, sub_prep1_i_score_result_end_term_0)

        main_prep_actual_total_blocks = int(main_prep1_info_end_term_0['totalBlocks'], 16)
        main_prep_actual_validate_blocks = int(main_prep1_info_end_term_0['validatedBlocks'], 16)
        self.assertEqual(0, main_prep_actual_total_blocks)
        self.assertEqual(0, main_prep_actual_validate_blocks)
        sub_prep_actual_total_blocks = int(sub_prep23_info_end_term_0['totalBlocks'], 16)
        sub_prep_actual_validate_blocks = int(sub_prep23_info_end_term_0['validatedBlocks'], 16)
        self.assertEqual(0, sub_prep_actual_total_blocks)
        self.assertEqual(0, sub_prep_actual_validate_blocks)

        # ################################ term 1 (26 ~ 47)
        # in the term 1
        term1_info: dict = self.get_iiss_info()
        term1_start_block_height = self._get_block_height() + 1
        print(f"###################################################################################################")
        print(f"Term 1 START - start BH: {term1_start_block_height}")
        print(f"Decentralization start")
        term1_rrep = int(term1_info["variable"]["rrep"], 16)
        term1_irep = int(term1_info["variable"]["irep"], 16)
        # expected rrep, irep is extracted from the excel
        expected_rrep = 1072
        expected_irep = 50000 * 10 ** 18
        # todo: check this value and if true, change to assert
        print("rrep: ", expected_rrep, term1_rrep)
        print("irep: ", expected_irep, term1_irep)
        # self.assertEqual(expected_rrep, term1_rrep)
        # self.assertEqual(expected_irep, term1_irep)

        term1_total_supply: int = self.icon_service.get_total_supply()
        term1_treausury_balance: int = self.get_balance(treausury_address)

        term1_end_block_height: int = self._make_blocks_to_end_calculation()
        print(f'Term 1 End - end BH: {term1_end_block_height}')
        total_supply_end_term_1: int = self.icon_service.get_total_supply()
        treasury_balance_end_term_1: int = self.get_balance(treausury_address)
        issue_data_of_term1, calulated_issue_amount_of_term1, actual_issue_amount_of_term1 = \
            self.get_issue_info_after_decentralized(term1_start_block_height, term1_end_block_height)
        cumulatived_covered_fee_of_term1 = sum([issue_data[2] for issue_data in issue_data_of_term1])

        expected_total_issue_amount_of_term_1 = 202_620_594_000_000_000_000
        print("calculated issue amount of term 1: ", expected_total_issue_amount_of_term_1,
              calulated_issue_amount_of_term1)
        # As no diff between IS-RC at the term 0,
        # coverted_fee + actual issue amount should equal to calculated issue amount of term0
        diff_between_is_and_rc_in_term_0 = issue_data_of_term1[-1][3]
        print("diff between IS and RC in term 0: ", 0, diff_between_is_and_rc_in_term_0)
        print("issue amount check: ",
              actual_issue_amount_of_term1 + cumulatived_covered_fee_of_term1, calulated_issue_amount_of_term1)

        treasury_balance_end_term_1: int = self.get_balance(treausury_address)
        total_supply_end_term_1: int = self.icon_service.get_total_supply()
        iconist_i_score_result_end_term_1 = int(self.query_iscore(iconist)['estimatedICX'], 16)
        total_iscore_of_all_iconist_end_term_1 = sum(
            map(lambda iconist: int(self.query_iscore(iconist)['estimatedICX'], 16), iconist_accounts))
        main_prep1_i_score_result_end_term_1 = int(self.query_iscore(main_prep1)['estimatedICX'], 16)
        main_prep1_info_end_term_1 = self.get_prep(main_prep1)
        sub_prep1_i_score_result_end_term_1 = int(self.query_iscore(sub_prep23)['estimatedICX'], 16)
        sub_prep23_info_end_term_1 = self.get_prep(sub_prep23)
        # todo: check this value and if true, change to assert
        # from excel
        expected_total_iconist_i_score_of_term_0 = 110124361111111000000
        print("total iconist iscore reward about term 0: ",
              expected_total_iconist_i_score_of_term_0, total_iscore_of_all_iconist_end_term_1)
        expected_main_prep_iscore_of_term_0 = 0
        print("main prep iscore reward about term 0: ",
              expected_main_prep_iscore_of_term_0, main_prep1_i_score_result_end_term_1)
        # self.assertEqual(expected_main_prep_iscore, main_prep1_i_score_result_end_term_1)
        # extracted from the excel
        expected_sub_prep_iscore_about_term_0 = 5_005_652_777_777_780_000
        expected_iconist_iscore_about_term_0 = 5_005_652_777_777_780_000
        print("sub prep iscore about term 0: ",
              expected_sub_prep_iscore_about_term_0, iconist_i_score_result_end_term_1)
        print("iconist prep iscore about term 0: ",
              expected_iconist_iscore_about_term_0, sub_prep1_i_score_result_end_term_1)
        # self.assertEqual(expected_sub_prep_iscore_about_term_0, iconist_i_score_result_end_term_1)
        # self.assertEqual(expected_iconist_iscore_about_term_0, sub_prep1_i_score_result_end_term_1)

        main_prep_actual_total_blocks = int(main_prep1_info_end_term_1['totalBlocks'], 16)
        main_prep_actual_validate_blocks = int(main_prep1_info_end_term_1['validatedBlocks'], 16)
        self.assertEqual(22, main_prep_actual_total_blocks)
        self.assertEqual(22, main_prep_actual_validate_blocks)
        sub_prep_actual_total_blocks = int(sub_prep23_info_end_term_1['totalBlocks'], 16)
        sub_prep_actual_validate_blocks = int(sub_prep23_info_end_term_1['validatedBlocks'], 16)
        self.assertEqual(0, sub_prep_actual_total_blocks)
        self.assertEqual(0, sub_prep_actual_validate_blocks)

        # ################################ term 2 (48 ~ 69)
        # in the term 2
        term2_info: dict = self.get_iiss_info()
        term2_start_block_height = self._get_block_height() + 1
        print(f"###################################################################################################")
        print(
            f"Term 2 START - start BH: {term2_start_block_height}")
        term2_rrep = int(term2_info["variable"]["rrep"], 16)
        term2_irep = int(term2_info["variable"]["irep"], 16)
        # expected rrep, irep is extracted from the excel
        expected_rrep = 1072
        expected_irep = 50000 * 10 ** 18
        # todo: check this value and if true, change to assert
        print("rrep:", expected_rrep, term2_rrep)
        print("irep:", expected_irep, term2_irep)
        # self.assertEqual(expected_rrep, term1_rrep)
        # self.assertEqual(expected_irep, term1_irep)

        term2_total_supply: int = self.icon_service.get_total_supply()
        term2_treausury_balance: int = self.get_balance(treausury_address)

        term2_end_block_height: int = self._make_blocks_to_end_calculation()
        print(f'Term 2 End - end BH: {term2_end_block_height}')
        total_supply_end_term_2: int = self.icon_service.get_total_supply()
        treasury_balance_end_term_2: int = self.get_balance(treausury_address)
        issue_data_of_term2, calulated_issue_amount_of_term2, actual_issue_amount_of_term2 = \
            self.get_issue_info_after_decentralized(term2_start_block_height, term2_end_block_height)
        cumulatived_covered_fee_of_term2 = sum([issue_data[2] for issue_data in issue_data_of_term2])

        treasury_balance_end_term_2: int = self.get_balance(treausury_address)
        total_supply_end_term_2: int = self.icon_service.get_total_supply()
        total_iscore_of_all_iconist_end_term_2 = sum(
            map(lambda iconist: int(self.query_iscore(iconist)['estimatedICX'], 16), iconist_accounts))
        iconist_i_score_result_end_term_2 = int(self.query_iscore(iconist)['estimatedICX'], 16)
        main_prep1_i_score_result_end_term_2 = int(self.query_iscore(main_prep1)['estimatedICX'], 16)
        main_prep1_info_end_term_2 = self.get_prep(main_prep1)
        sub_prep1_i_score_result_end_term_2 = int(self.query_iscore(sub_prep23)['estimatedICX'], 16)
        sub_prep23_info_end_term_2 = self.get_prep(sub_prep23)

        self.assertEqual(treasury_balance_end_term_2 - term2_treausury_balance,
                         actual_issue_amount_of_term2 + cumulatived_covered_fee_of_term2)
        self.assertEqual(total_supply_end_term_2 - term2_total_supply,
                         treasury_balance_end_term_2 - term2_treausury_balance - cumulatived_covered_fee_of_term2)
        # todo: check this value and if true, change to assert
        expected_total_iconist_i_score_about_term_1 = 144287385135802000000
        print("total iconist iscore reward about term 1: ",
              expected_total_iconist_i_score_about_term_1,
              total_iscore_of_all_iconist_end_term_2 - total_iscore_of_all_iconist_end_term_1)
        # self.assertEqual(expected_main_prep_iscore, main_prep1_i_score_result_end_term_1)
        # extracted from the excel
        # beta1 + beta2
        expected_main_prep_iscore_about_term_1 = 424_382_716_049_383_000 + 1_845_142_243_692_970_000
        # beta2 + beta3
        expected_sub_prep_iscore_about_term_1 = 1_845_142_243_692_970_000 + 6_558_517_506_172_840_000
        # beta3
        expected_iconist_iscore_about_term_1 = 6_558_517_506_172_840_000
        print("main prep iscore about term 1: ",
              expected_main_prep_iscore_about_term_1, main_prep1_i_score_result_end_term_2)
        print("iconist prep iscore about term 1: ",
              expected_iconist_iscore_about_term_1,
              iconist_i_score_result_end_term_2 - iconist_i_score_result_end_term_1)
        print("sub prep iscore about term 1: ",
              expected_sub_prep_iscore_about_term_1,
              sub_prep1_i_score_result_end_term_2 - sub_prep1_i_score_result_end_term_1)

        main_prep_actual_total_blocks = int(main_prep1_info_end_term_1['totalBlocks'], 16)
        main_prep_actual_validate_blocks = int(main_prep1_info_end_term_1['validatedBlocks'], 16)
        self.assertEqual(22, main_prep_actual_total_blocks)
        self.assertEqual(22, main_prep_actual_validate_blocks)
        sub_prep_actual_total_blocks = int(sub_prep23_info_end_term_1['totalBlocks'], 16)
        sub_prep_actual_validate_blocks = int(sub_prep23_info_end_term_1['validatedBlocks'], 16)
        self.assertEqual(0, sub_prep_actual_total_blocks)
        self.assertEqual(0, sub_prep_actual_validate_blocks)
