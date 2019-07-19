from typing import List, Dict

from iconservice.icon_constant import IISS_ANNUAL_BLOCK, ISCORE_EXCHANGE_RATE
from iconservice.icx.issue.issue_formula import IssueFormula

from test_suite.json_rpc_api.base import Base, ICX_FACTOR
from test_suite.json_rpc_api.base import TestAccount

MIN_DELEGATION = 788_400
min_rrep = 200
gv_divider = 10_000
reward_divider = IISS_ANNUAL_BLOCK * gv_divider // ISCORE_EXCHANGE_RATE


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

    def test_iscore(self):
        init_balance: int = 3000 * ICX_FACTOR
        stake_value: int = MIN_DELEGATION
        account_count: int = 2
        accounts: List['TestAccount'] = self.create_accounts(account_count)

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

        # increase block height to 1st calculation
        calculate1_block_height: int = self._make_blocks_to_end_calculation()
        # calculate IScore with rrep at calculate1_block_height
        iscore1: int = self._calculate_iscore(delegation_value, delegation_block, calculate1_block_height)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to 2nd calculation
        calculate2_block_height: int = self._make_blocks_to_end_calculation()
        iscore2: int = self._calculate_iscore(delegation_value, calculate1_block_height, calculate2_block_height)

        # queryIScore
        response: dict = self.query_iscore(accounts[0])
        self.assertEqual(hex(iscore1), response['iscore'])
        self.assertEqual(hex(calculate1_block_height), response['blockHeight'])

        # increase block height to 3rd calculation
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
