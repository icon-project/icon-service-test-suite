from time import sleep
from typing import List, Dict, TYPE_CHECKING

from iconservice.icon_constant import IISS_ANNUAL_BLOCK, ISCORE_EXCHANGE_RATE
from iconservice.icx.issue.issue_formula import IssueFormula

from test_suite.json_rpc_api.base import Base, ICX_FACTOR

if TYPE_CHECKING:
    from iconsdk.builder.transaction_builder import Transaction
    from iconsdk.signed_transaction import SignedTransaction
    from ..base import Account

min_rrep = 200
gv_divider = 10_000
reward_divider = IISS_ANNUAL_BLOCK * gv_divider // ISCORE_EXCHANGE_RATE
MIN_DELEGATION = int(IISS_ANNUAL_BLOCK / ISCORE_EXCHANGE_RATE * (gv_divider / min_rrep))


class TestIScore(Base):

    def _calculate_iscore(self, delegation: int, st: int, ed: int) -> int:
        if delegation < MIN_DELEGATION:
            return 0

        iiss_info = self.get_iiss_info()
        rrep = int(iiss_info['variable'].get('rrep'), 16)
        if rrep < min_rrep:
            return 0

        new_rrep: int = IssueFormula.calculate_temporary_reward_prep(rrep)
        # iscore = delegation_amount * period * rrep / reward_divider
        return int(delegation * new_rrep * (ed - st) / reward_divider)

    def test_iscore1(self):
        init_balance: int = 3000 * ICX_FACTOR
        stake_value: int = MIN_DELEGATION
        account_count: int = 2
        accounts: List['Account'] = self.create_accounts(account_count)

        self.distribute_icx(accounts, init_balance)

        # register P-Rep
        self.register_prep(accounts[1:])

        # setStake
        self.set_stake(accounts[:1], stake_value)

        # getStake
        response: dict = self.get_stake(accounts[0])
        expect_result: dict = {
            "stake": hex(stake_value),
        }
        self.assertEqual(expect_result, response)

        # delegate to P-Rep
        delegation_value: int = stake_value
        origin_delegations: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations)
        delegation_block = self._get_block_height()

        # query delegation
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations[user_id])
        expect_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(delegation_value),
            "votingPower": hex(stake_value - delegation_value)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expect_result, response)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to end of 1st calculation
        calculate1_block_height: int = self._make_blocks_to_end_calculation()
        # calculate IScore with rrep at calculate1_block_height
        iscore1: int = self._calculate_iscore(delegation_value, delegation_block, calculate1_block_height)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to end of 2nd calculation
        calculate2_block_height: int = self._make_blocks_to_end_calculation()
        iscore2: int = self._calculate_iscore(delegation_value, calculate1_block_height, calculate2_block_height)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(iscore1), response['iscore'])
        self.assertEqual(hex(calculate1_block_height), response['blockHeight'])

        # increase block height to end of 3rd calculation
        calculate3_block_height: int = self._make_blocks_to_end_calculation()
        iscore3: int = self._calculate_iscore(delegation_value, calculate2_block_height, calculate3_block_height)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(iscore1 + iscore2), response['iscore'])
        self.assertEqual(hex(calculate2_block_height), response['blockHeight'])

        # claimIScore
        self.claim_iscore(accounts)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        iscore_after_claim: int = (iscore1 + iscore2) % 1000
        self.assertEqual(hex(iscore_after_claim), response['iscore'])
        self.assertEqual(hex(calculate2_block_height), response['blockHeight'])

        # increase block height to 4th calculation
        self._make_blocks_to_end_calculation()

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(iscore_after_claim + iscore3), response['iscore'])
        self.assertEqual(hex(calculate3_block_height), response['blockHeight'])

        # refund icx
        self.refund_icx(accounts)

    def test_iscore2(self):
        init_balance: int = 3000 * ICX_FACTOR
        stake_value: int = MIN_DELEGATION
        account_count: int = 2
        accounts: List['Account'] = self.create_accounts(account_count)

        self.distribute_icx(accounts, init_balance)

        # register P-Rep
        self.register_prep(accounts[1:])

        # setStake
        self.set_stake(accounts[:1], stake_value)

        # getStake
        response: dict = self.get_stake(accounts[0])
        expect_result: dict = {
            "stake": hex(stake_value),
        }
        self.assertEqual(expect_result, response)

        # delegate to P-Rep
        delegation_value: int = stake_value
        origin_delegations: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations)

        # query delegation
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations[user_id])
        expect_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(delegation_value),
            "votingPower": hex(stake_value - delegation_value)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expect_result, response)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(0), response['iscore'])
        self._make_blocks_to_end_calculation()
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(0), response['iscore'])

        last_iscore: int = 0
        for i in range(1):
            self._make_blocks_to_end_calculation()
            response: dict = self.query_iscore(accounts[0])
            iscore: int = int(response['iscore'], 16)
            self.assertNotEqual(0, iscore)
            self.assertNotEqual(last_iscore, iscore)
            last_iscore: int = iscore

        # refund icx
        self.refund_icx(accounts)

    def test_iscore3(self):
        init_balance: int = 3000 * ICX_FACTOR
        stake_value: int = 1 * ICX_FACTOR
        account_count: int = 2
        accounts: List['Account'] = self.create_accounts(account_count)

        self.distribute_icx(accounts, init_balance)

        # register P-Rep
        self.register_prep(accounts[1:])

        # setStake
        self.set_stake(accounts[:1], stake_value)

        # getStake
        response: dict = self.get_stake(accounts[0])
        expect_result: dict = {
            "stake": hex(stake_value),
        }
        self.assertEqual(expect_result, response)

        # delegate to P-Rep
        delegation_value: int = stake_value
        origin_delegations: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations)
        delegation_block = self._get_block_height()

        # query delegation
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations[user_id])
        expect_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(delegation_value),
            "votingPower": hex(stake_value - delegation_value)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expect_result, response)

        self._make_blocks_to_end_calculation()

        for i in range(10):
            self._make_blocks_to_end_calculation()
            self.claim_iscore(accounts)

        # refund icx
        self.refund_icx(accounts)

    def test_iscore4(self):
        init_balance: int = 20000 * ICX_FACTOR
        stake_value: int = 10000 * ICX_FACTOR
        account_count: int = 2
        accounts: List['Account'] = self.create_accounts(account_count)

        self.distribute_icx(accounts, init_balance)

        # register P-Rep
        self.register_prep(accounts[1:])

        # setStake
        self.set_stake(accounts[:1], stake_value)

        # getStake
        response: dict = self.get_stake(accounts[0])
        expect_result: dict = {
            "stake": hex(stake_value),
        }
        self.assertEqual(expect_result, response)

        # delegate to P-Rep
        delegation_value: int = 2000 * ICX_FACTOR
        origin_delegations: list = []
        for i, account in enumerate(accounts):
            origin_delegations.append((account, delegation_value * (i+1)))
        self.set_delegation(accounts[:1], [origin_delegations])

        self._make_blocks_to_end_calculation()
        self._make_blocks_to_end_calculation()

        for i in range(10):
            self._make_blocks_to_end_calculation()
            self.claim_iscore(accounts)
            response: dict = self.query_iscore(accounts[0])
            self.assertTrue(int(response['iscore'], 16) < 1000)

        # refund icx
        self.refund_icx(accounts)

    def test_iscore_event_log_and_estimate_fee(self):
        init_balance: int = 3000 * ICX_FACTOR
        stake_value: int = MIN_DELEGATION * 10
        account_count: int = 2
        accounts: List['Account'] = self.create_accounts(account_count)

        self.distribute_icx(accounts, init_balance)

        # register P-Rep
        self.register_prep(accounts[1:])

        # setStake
        self.set_stake(accounts[:1], stake_value)

        # getStake
        response: dict = self.get_stake(accounts[0])
        expect_result: dict = {
            "stake": hex(stake_value),
        }
        self.assertEqual(expect_result, response)

        # delegate to P-Rep
        delegation_value: int = stake_value
        origin_delegations: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations)
        delegation_block = self._get_block_height()

        # query delegation
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations[user_id])
        expect_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(delegation_value),
            "votingPower": hex(stake_value - delegation_value)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expect_result, response)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to end of 1st calculation
        calculate1_block_height: int = self._make_blocks_to_end_calculation()
        # calculate IScore with rrep at calculate1_block_height
        iscore1: int = self._calculate_iscore(delegation_value, delegation_block, calculate1_block_height)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to end of 2nd calculation
        calculate2_block_height: int = self._make_blocks_to_end_calculation()
        iscore2: int = self._calculate_iscore(delegation_value, calculate1_block_height, calculate2_block_height)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(iscore1), response['iscore'])
        self.assertEqual(hex(calculate1_block_height), response['blockHeight'])

        # increase block height to end of 3rd calculation
        calculate3_block_height: int = self._make_blocks_to_end_calculation()
        _: int = self._calculate_iscore(delegation_value, calculate2_block_height, calculate3_block_height)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(iscore1 + iscore2), response['iscore'])
        self.assertEqual(hex(calculate2_block_height), response['blockHeight'])

        # estimate
        tx: 'Transaction' = self.create_claim_iscore_tx_without_sign(accounts[0])
        estimate_step: int = self.estimate_step(tx)
        step_price: int = self.get_step_price()
        estimate_fee: int = step_price * estimate_step

        account_1_balance_before_claim: int = accounts[0].balance

        # claimIScore
        tx_list: list = []
        tx: 'SignedTransaction' = self.create_claim_iscore_tx(accounts[0])
        tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        expected_claimed_icx = (iscore1 + iscore2) // 1000
        expected_claimed_iscore = expected_claimed_icx * 1000

        claimed_icx: str = tx_results[0]['eventLogs'][0]["data"][1]
        self.assertEqual('IScoreClaimed(int,int)', tx_results[0]['eventLogs'][0]["indexed"][0])
        self.assertEqual(hex(expected_claimed_iscore), tx_results[0]['eventLogs'][0]["data"][0])
        self.assertEqual(hex(expected_claimed_icx), claimed_icx)
        accounts[0].balance += int(claimed_icx, 16)
        accounts[0].balance -= tx_results[0]['stepUsed'] * tx_results[0]['stepPrice']

        expected_balance: int = account_1_balance_before_claim + expected_claimed_icx - estimate_fee - stake_value
        actual_balance: int = self.get_balance(accounts[0])
        self.assertEqual(expected_balance, actual_balance)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(iscore1 + iscore2 - expected_claimed_iscore), response['iscore'])

        # refund icx
        self.refund_icx(accounts)

    # TODO remove
    # def test_iscore3(self):
    #     init_balance: int = 10_000 * ICX_FACTOR
    #     stake_value: int = 5_000 * ICX_FACTOR
    #     account_count: int = 2
    #     accounts: List['Account'] = self.create_accounts(account_count)
    #
    #     self.distribute_icx(accounts, init_balance)
    #
    #     # register P-Rep
    #     self.register_prep(accounts[1:])
    #
    #     # setStake
    #     self.set_stake(accounts[:1], stake_value)
    #
    #     # getStake
    #     response: dict = self.get_stake(accounts[0])
    #     expect_result: dict = {
    #         "stake": hex(stake_value),
    #     }
    #     self.assertEqual(expect_result, response)
    #
    #     # delegate to P-Rep
    #     delegation_value: int = stake_value
    #     origin_delegations: list = [[(accounts[1], delegation_value)]]
    #     self.set_delegation(accounts[:1], origin_delegations)
    #
    #     # query delegation
    #     user_id: int = 0
    #     expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations[user_id])
    #     expect_result: dict = {
    #         "delegations": expected_delegations,
    #         "totalDelegated": hex(delegation_value),
    #         "votingPower": hex(stake_value - delegation_value)
    #     }
    #     response: dict = self.get_delegation(accounts[user_id])
    #     self.assertEqual(expect_result, response)
    #
    #     # queryIScore
    #     response: dict = self.query_iscore(accounts[0])
    #     self.assertEqual(hex(0), response['iscore'])
    #
    #     # test
    #     expected: list = []
    #     actual: list = []
    #     for i in range(10):
    #         start_block = self._get_block_height()
    #         end_block: int = self._make_blocks_to_end_calculation()
    #         actual_end_block: int = self.icon_service.get_block("latest")["height"]
    #         self.assertEqual(end_block, actual_end_block)
    #         iscore: int = self._calculate_iscore(delegation_value, start_block, end_block)
    #         expected.append(iscore)
    #         response: dict = self.query_iscore(accounts[0])
    #         actual.append(int(response['iscore'], 16))
    #     expected = expected[:-2]
    #     for i in range(2, len(actual)):
    #         actual[i - 2] = actual[i] - actual[i - 1]
    #     actual = actual[:-2]
    #
    #     print("expected", expected)
    #     print("actual", actual)
    #
    #     # refund icx
    #     self.refund_icx(accounts)
    #
    # def test_iscore4(self):
    #     init_balance: int = 10_000 * ICX_FACTOR
    #     stake_value: int = 5_000 * ICX_FACTOR
    #     account_count: int = 1
    #     accounts: List['Account'] = self.create_accounts(account_count)
    #
    #     self.distribute_icx(accounts, init_balance)
    #
    #     # register P-Rep
    #     self.register_prep(accounts)
    #
    #     # setStake
    #     self.set_stake(accounts[:1], stake_value)
    #
    #     # getStake
    #     response: dict = self.get_stake(accounts[0])
    #     expect_result: dict = {
    #         "stake": hex(stake_value),
    #     }
    #     self.assertEqual(expect_result, response)
    #
    #     # delegate to P-Rep
    #     delegation_value: int = stake_value
    #     origin_delegations: list = [[(accounts[0], delegation_value)]]
    #     self.set_delegation(accounts[:1], origin_delegations)
    #
    #     # query delegation
    #     user_id: int = 0
    #     expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations[user_id])
    #     expect_result: dict = {
    #         "delegations": expected_delegations,
    #         "totalDelegated": hex(delegation_value),
    #         "votingPower": hex(stake_value - delegation_value)
    #     }
    #     response: dict = self.get_delegation(accounts[user_id])
    #     self.assertEqual(expect_result, response)
    #
    #     # queryIScore
    #     response: dict = self.query_iscore(accounts[0])
    #     self.assertEqual(hex(0), response['iscore'])
    #
    #     # test
    #     # queryIScore
    #     actual: list = []
    #     for i in range(10):
    #         end_block: int = self._make_blocks_to_end_calculation()
    #         actual_end_block: int = self.icon_service.get_block("latest")["height"]
    #         self.assertEqual(end_block, actual_end_block)
    #         response: dict = self.query_iscore(accounts[0])
    #         actual.append(int(response['iscore'], 16))
    #
    #     for i in range(2, len(actual)):
    #         actual[i - 2] = actual[i] - actual[i - 1]
    #     actual = actual[:-2]
    #     print(actual)