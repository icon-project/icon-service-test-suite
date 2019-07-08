from typing import List, Dict, Tuple, TYPE_CHECKING

from iconsdk.signed_transaction import SignedTransaction
from iconservice.base.type_converter_templates import ConstantKeys
from iconservice.icon_constant import REV_DECENTRALIZATION

from .base import Base

if TYPE_CHECKING:
    from iconsdk.wallet.wallet import KeyWallet


class TestDecentralization(Base):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    @staticmethod
    def create_prep_params(params: List[Tuple['KeyWallet', int]]) -> List[Dict[str, str]]:
        return [{"address": key_wallet.get_address(), "delegated": hex(value)}
                for (key_wallet, value) in params]

    def test_decentralization(self):
        name: int = 0
        params = {
            ConstantKeys.NAME: f"{name}",
            ConstantKeys.EMAIL: f"node{name}@example.com",
            ConstantKeys.WEBSITE: f"https://node{name}.example.com",
            ConstantKeys.DETAILS: f"https://node{name}.example.com/details",
            ConstantKeys.P2P_END_POINT: f"https://node{name}.example.com:7100",
            ConstantKeys.PUBLIC_KEY: f"0x{self._wallet_array[name].bytes_public_key.hex()}"
        }
        tx = self.create_register_prep_tx(self._wallet_array[name], params, step_limit=10000000)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(True, tx_result['status'])

        balance: int = 100
        origin_delegator: List[Tuple['KeyWallet', int]] = [(self._wallet_array[name], balance)]

        tx_list: list = []
        tx: 'SignedTransaction' = self.create_set_stake_tx(self._wallet_array[name], balance)
        tx_list.append(tx)
        tx: 'SignedTransaction' = self.create_set_delegation_tx(self._wallet_array[name],
                                                                origin_delegator)
        tx_list.append(tx)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        response: dict = self.get_main_prep_list()
        expected: dict = {
            'totalDelegated': hex(0),
            'preps': []
        }
        self.assertEqual(expected, response)

        tx: 'SignedTransaction' = self.create_set_revision_tx(self._test1, REV_DECENTRALIZATION)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertEqual(True, tx_result['status'])

        expected_prep: List[Dict[str, str]] = self.create_prep_params(origin_delegator)
        response: dict = self.get_main_prep_list()
        expected: dict = {
            'totalDelegated': hex(balance),
            'preps': expected_prep
        }
        self.assertEqual(expected, response)
        print(response)

        # reg prep1
        name: int = 1
        params = {
            ConstantKeys.NAME: f"{name}",
            ConstantKeys.EMAIL: f"node{name}@example.com",
            ConstantKeys.WEBSITE: f"https://node{name}.example.com",
            ConstantKeys.DETAILS: f"https://node{name}.example.com/details",
            ConstantKeys.P2P_END_POINT: f"https://node{name}.example.com:7100",
            ConstantKeys.PUBLIC_KEY: f"0x{self._wallet_array[name].bytes_public_key.hex()}"
        }
        tx = self.create_register_prep_tx(self._wallet_array[name], params, step_limit=10000000)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(True, tx_result['status'])

        # set stake and delegate prep1
        balance: int = 200
        origin_delegator: List[Tuple['KeyWallet', int]] = [(self._wallet_array[name], balance)]

        tx_list: list = []
        tx: 'SignedTransaction' = self.create_set_stake_tx(self._wallet_array[name], balance)
        tx_list.append(tx)
        tx: 'SignedTransaction' = self.create_set_delegation_tx(self._wallet_array[name],
                                                                origin_delegator)
        tx_list.append(tx)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        self._make_blocks_to_next_calculation()

        expected_prep: List[Dict[str, str]] = self.create_prep_params(origin_delegator)
        response: dict = self.get_main_prep_list()
        expected: dict = {
            'totalDelegated': hex(balance),
            'preps': expected_prep
        }
        self.assertEqual(expected, response)
        print(response)