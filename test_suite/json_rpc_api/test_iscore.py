from iconsdk.wallet.wallet import KeyWallet

from .base import Base

min_rrep = 200
min_delegation = 788400
block_per_year = 15768000
gv_divider = 10000
iscore_multiplier = 1000
reward_divider = block_per_year * gv_divider / iscore_multiplier


class TestIScore(Base):
    MIN_DELEGATION = 788_400

    def setUp(self):
        super().setUp()

    def _calculate_iscore(self, delegation, from_, to) -> int:
        if delegation < min_delegation:
            return 0

        iiss_info = self.get_iiss_info()
        rrep = int(iiss_info['variable'].get('rrep'), 16)
        if rrep < min_rrep:
            return 0

        # iscore = delegation_amount * period * rrep / reward_divider
        return int(delegation * rrep * (to - from_) / reward_divider)

    def test_iscore(self):
        stake_value: int = self.MIN_DELEGATION * 1000
        delegation_value: int = self.MIN_DELEGATION * 100
        account = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1, account.get_address(), stake_value + 10**18)
        self.process_transaction(tx, self.icon_service)
        prep = self._test1

        # register P-Rep
        params = {"name": "prep_test",
                  "email": "prep_test@test.com", "website": "https://prep_test.com",
                  "details": "https://detail.prep_test.com",
                  "p2pEndPoint": "target://prep_test.com:7100",
                  "publicKey": f'0x{prep.bytes_public_key.hex()}'
                  }
        tx = self.create_register_prep_tx(prep, params)
        self.process_transaction(tx, self.icon_service)
        # setStake

        tx = self.create_set_stake_tx(account, stake_value)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        # getStake
        response = self.get_stake(account)

        expect_result = {
            "stake": hex(stake_value),
        }
        self.assertEqual(expect_result, response)

        # delegate to P-Rep
        delegations = [(prep, delegation_value)]
        delegation_params = self.create_delegation_params(delegations)
        tx = self.create_set_delegation_tx(account, delegations)
        tx_result = self.process_transaction(tx, self.icon_service)
        delegation_block = tx_result['blockHeight']

        # query delegation
        response = self.get_delegation(account)
        expect_result = {
            "delegations": delegation_params,
            "totalDelegated": hex(delegation_value),
            "votingPower": hex(stake_value - delegation_value)
        }
        self.assertEqual(expect_result, response)

        # queryIScore
        response = self.query_iscore(account)
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to 1st calculation
        calculate1_block_height = self._make_blocks_to_next_calculation()
        # calculate IScore with rrep at calculate1_block_height
        iscore1 = self._calculate_iscore(delegation_value, delegation_block, calculate1_block_height)

        # queryIScore
        response = self.query_iscore(account)
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to 2nd calculation
        calculate2_block_height = self._make_blocks_to_next_calculation()
        iscore2 = self._calculate_iscore(delegation_value, calculate1_block_height, calculate2_block_height)

        # queryIScore
        response = self.query_iscore(account)
        self.assertEqual(hex(iscore1), response['iscore'])
        self.assertEqual(hex(calculate1_block_height), response['blockHeight'])

        # increase block height to 3rd calculation
        calculate3_block_height = self._make_blocks_to_next_calculation()
        iscore3 = self._calculate_iscore(delegation_value, calculate2_block_height, calculate3_block_height)

        # queryIScore
        response = self.query_iscore(account)
        self.assertEqual(hex(iscore1 + iscore2), response['iscore'])
        self.assertEqual(hex(calculate2_block_height), response['blockHeight'])

        # claimIScore
        tx = self.create_claim_iscore_tx(account)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        # queryIScore
        response = self.query_iscore(account)
        iscore_after_claim = (iscore1 + iscore2) % 1000
        self.assertEqual(hex(iscore_after_claim), response['iscore'])
        self.assertEqual(hex(calculate2_block_height), response['blockHeight'])

        # increase block height to 4th calculation
        self._make_blocks_to_next_calculation()

        # queryIScore
        response = self.query_iscore(account)
        self.assertEqual(hex(iscore_after_claim + iscore3), response['iscore'])
        self.assertEqual(hex(calculate3_block_height), response['blockHeight'])
