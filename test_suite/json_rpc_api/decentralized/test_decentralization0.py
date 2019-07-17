from typing import List, Dict, Tuple, TYPE_CHECKING

from iconsdk.signed_transaction import SignedTransaction
from iconservice.icon_constant import REV_DECENTRALIZATION, PREP_MAIN_PREPS

from test_suite.json_rpc_api.base import Base

if TYPE_CHECKING:
    from iconsdk.wallet.wallet import KeyWallet


class TestDecentralization(Base):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    def test_func(self):
        total_supply: int = self.icon_service.get_total_supply()
        base_balance: int = self.get_balance(self._wallet_array[0])
        # Minimum_delegate_amount is 0.02 * total_supply
        # In this test delegate 0.03*total_supply because `Issue transaction` exists since REV_IISS
        minimum_delegate_amount_for_decentralization: int = total_supply * 2 // 1000 + 1
        init_balance: int = minimum_delegate_amount_for_decentralization * 10

        # distribute icx PREP_MAIN_PREPS ~ PREP_MAIN_PREPS + PREP_MAIN_PREPS - 1
        tx_list: list = []
        for i in range(PREP_MAIN_PREPS):
            tx: dict = self.create_transfer_icx_tx(self._test1,
                                                   self._wallet_array[PREP_MAIN_PREPS + i],
                                                   init_balance)
            tx_list.append(tx)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # stake PREP_MAIN_PREPS ~ PREP_MAIN_PREPS + PREP_MAIN_PREPS - 1
        stake_amount: int = minimum_delegate_amount_for_decentralization
        tx_list: list = []
        for i in range(PREP_MAIN_PREPS):
            tx: dict = self.create_set_stake_tx(self._wallet_array[PREP_MAIN_PREPS + i],
                                                stake_amount)
            tx_list.append(tx)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # register PRep
        tx_list: list = []
        for address in self._wallet_array[:PREP_MAIN_PREPS]:
            tx: dict = self.create_register_prep_tx(address)
            tx_list.append(tx)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # delegate to PRep
        tx_list: list = []
        for i in range(PREP_MAIN_PREPS):
            tx: dict = self.create_set_delegation_tx(self._wallet_array[PREP_MAIN_PREPS + i],
                                                     [
                                                         (
                                                             self._wallet_array[i],
                                                             minimum_delegate_amount_for_decentralization
                                                         )
                                                     ])
            tx_list.append(tx)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # get main prep
        response: dict = self.get_main_prep_list()
        expected_response: dict = {
            "preps": [],
            "totalDelegated": hex(0)
        }
        self.assertEqual(expected_response, response)

        # set Revision REV_IISS (decentralization)
        tx: 'SignedTransaction' = self.create_set_revision_tx(self._test1, REV_DECENTRALIZATION)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get main prep
        response: dict = self.get_main_prep_list()
        expected_preps: list = []
        expected_total_delegated: int = 0
        for wallet in self._wallet_array[:PREP_MAIN_PREPS]:
            expected_preps.append({
                'address': wallet.get_address(),
                'delegated': hex(minimum_delegate_amount_for_decentralization)
            })
            expected_total_delegated += minimum_delegate_amount_for_decentralization
        expected_response: dict = {
            "preps": expected_preps,
            "totalDelegated": hex(expected_total_delegated)
        }
        self.assertEqual(expected_response, response)

        # delegate to PRep 0
        tx_list: list = []
        for i in range(PREP_MAIN_PREPS):
            tx: dict = self.create_set_delegation_tx(self._wallet_array[PREP_MAIN_PREPS + i], [])
            tx_list.append(tx)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        self._make_blocks_to_next_calculation()

        # get main prep
        response: dict = self.get_main_prep_list()
        expected_preps: list = []
        for wallet in self._wallet_array[:PREP_MAIN_PREPS]:
            expected_preps.append({
                'address': wallet.get_address(),
                'delegated': hex(0)
            })
        expected_response: dict = {
            "preps": expected_preps,
            "totalDelegated": hex(0)
        }
        self.assertEqual(expected_response, response)
