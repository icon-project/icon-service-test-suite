from typing import TYPE_CHECKING, List, Tuple, Dict

from iconsdk.wallet.wallet import KeyWallet
from iconservice.icon_constant import IISS_ANNUAL_BLOCK, ISCORE_EXCHANGE_RATE
from iconservice.icx.issue.issue_formula import IssueFormula

from ..base import Base, ICX_FACTOR

if TYPE_CHECKING:
    from iconsdk.signed_transaction import SignedTransaction

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
        init_account_count: int = 2

        accounts: List['KeyWallet'] = [KeyWallet.create() for _ in range(init_account_count)]

        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, account.get_address(), init_balance)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # register P-Rep
        tx: 'SignedTransaction' = self.create_register_prep_tx(accounts[1])
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # setStake
        tx: 'SignedTransaction' = self.create_set_stake_tx(accounts[0], stake_value)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # getStake
        response: dict = self.get_stake(accounts[0])
        expect_result: dict = {
            "stake": hex(stake_value),
        }
        self.assertEqual(expect_result, response)

        # delegate to P-Rep
        delegation_value: int = stake_value
        origin_delegations: List[Tuple['KeyWallet', int]] = [(accounts[1], delegation_value)]
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        delegation_block = tx_result['blockHeight']

        # query delegation
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        response: dict = self.get_delegation(accounts[0])
        expect_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(delegation_value),
            "votingPower": hex(stake_value - delegation_value)
        }
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
        tx: 'SignedTransaction' = self.create_claim_iscore_tx(accounts[0])
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

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
