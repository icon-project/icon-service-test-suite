from typing import List, Tuple, Dict, TYPE_CHECKING

from test_suite.json_rpc_api.base import Base, ICX_FACTOR, PREP_REGISTER_COST_ICX, TestAccount

if TYPE_CHECKING:
    from iconsdk.signed_transaction import SignedTransaction


class TestPRep(Base):

    def test_1_register_one_prep_invalid_case1(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        account_count: int = 1
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        account = accounts[0]

        # create
        self.distribute_icx(accounts, init_balance)

        # register prep with unfilled data
        register_data = self._create_register_prep_params(account)
        del register_data['p2pEndpoint']
        tx: 'SignedTransaction' = self.create_register_prep_tx(account, register_data)
        tx_hashes: list = self.process_transaction_bulk_without_txresult([tx], self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(False, tx_result['status'])
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        get_prep_response = self.get_prep(account)
        self.assertTrue(get_prep_response['message'].startswith('P-Rep not found'))

        # refund icx
        self.refund_icx(accounts)

    def test_2_register_one_prep_invalid_case2(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        account_count: int = 1
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        account = accounts[0]

        # create
        self.distribute_icx(accounts, init_balance)

        # register prep with unfilled data
        register_data = self._create_register_prep_params(account)
        register_data['name'] = ' '
        tx: 'SignedTransaction' = self.create_register_prep_tx(account, register_data)
        tx_hashes: list = self.process_transaction_bulk_without_txresult([tx], self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(False, tx_result['status'])
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        get_prep_response = self.get_prep(account)
        self.assertTrue(get_prep_response['message'].startswith('P-Rep not found'))

        # refund icx
        self.refund_icx(accounts)

    def test_3_register_one_prep(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        account_count: int = 1
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        account = accounts[0]

        # create
        self.distribute_icx(accounts, init_balance)

        self.register_prep(accounts)
        # set prep on pre-voting
        set_prep_data = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "http://banana.com/detail",
            "p2pEndpoint": "123.213.123.123:7100"
        }
        tx = self.create_set_prep_tx(account, set_data=set_prep_data)
        tx_hashes: List['SignedTransaction'] = self.process_transaction_bulk_without_txresult([tx], self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(True, tx_result['status'])
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        prep_data = self.get_prep(account)
        self.assertEqual(prep_data['name'], set_prep_data['name'])
        self.assertEqual(prep_data['email'], set_prep_data['email'])
        self.assertEqual(prep_data['website'], set_prep_data['website'])
        self.assertEqual(prep_data['details'], set_prep_data['details'])
        self.assertEqual(prep_data['p2pEndpoint'], set_prep_data['p2pEndpoint'])

        # set irep on pre-voting
        irep = 40000
        params = {
            "name": "apple node2",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "http://banana.com/detail",
            "p2pEndpoint": "123.213.123.123:7100",
        }
        tx = self.create_set_prep_tx(account, irep, params)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(False, tx_result['status'])
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        prep_data = self.get_prep(account)
        self.assertEqual(prep_data['name'], set_prep_data['name'])
        self.assertEqual(prep_data['email'], set_prep_data['email'])
        self.assertEqual(prep_data['website'], set_prep_data['website'])
        self.assertEqual(prep_data['details'], set_prep_data['details'])
        self.assertEqual(prep_data['p2pEndpoint'], set_prep_data['p2pEndpoint'])
        self.assertNotEqual(prep_data['irep'], hex(irep))

        # refund icx
        self.refund_icx(accounts)

    def test_4_register_100_preps_and_check_total_delegated(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 10) * ICX_FACTOR
        account_count: int = 110
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        preps: List['TestAccount'] = accounts[:100]
        iconists: List['TestAccount'] = accounts[100:]
        stake_value: int = 100

        initial_total_delegated: int = int(self.get_prep_list()['totalDelegated'], 16)

        # create
        self.distribute_icx(accounts, init_balance)

        # register preps
        self.register_prep(accounts)

        # stake
        self.set_stake(iconists, stake_value)

        # delegate
        # set delegation
        origin_delegations_list: list = []
        expected_delegation_values: dict = {}
        for i, wallet in enumerate(iconists):
            origin_delegations: List[Tuple['TestAccount', int]] = []

            delegation_value: int = stake_value
            expected_delegation_values[i] = delegation_value
            origin_delegations.append((preps[i], delegation_value))

            origin_delegations_list.append(origin_delegations)
        self.set_delegation(iconists, origin_delegations_list)

        # get delegation
        for i, wallet in enumerate(iconists):
            expected_total_delegation: int = 0
            for delegation in origin_delegations_list[i]:
                expected_total_delegation += delegation[1]
            expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[i])
            expected_voting_power: int = stake_value - expected_total_delegation
            expected_result: dict = {
                "delegations": expected_delegations,
                "totalDelegated": hex(expected_total_delegation),
                "votingPower": hex(expected_voting_power)
            }
            response: dict = self.get_delegation(wallet)
            self.assertEqual(expected_result, response)

        # get preps and check total_delegated
        total_delegated = int(self.get_prep_list()['totalDelegated'], 16)
        self.assertEqual(initial_total_delegated + 10 * len(preps), total_delegated)

        # refund icx
        self.refund_icx(accounts)
