from iconsdk.wallet.wallet import KeyWallet

from test_suite.json_rpc_api.base import Base, ICX_FACTOR, PREP_REGISTER_COST_ICX


class TestPRep(Base):

    def test_1_register_one_prep_invalid_case1(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        wallet = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1,
                                         wallet.get_address(),
                                         init_balance)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "http://banana.com/detail",
            "publicKey": f"0x{wallet.bytes_public_key.hex()}"
        }
        tx = self.create_register_prep_tx(wallet, params)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(False, tx_result['status'])

        response = self.get_prep(wallet)
        self.assertTrue(response['message'].startswith('P-Rep not found'))

    def test_2_register_one_prep_invalid_case2(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        wallet = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1,
                                         wallet.get_address(),
                                         init_balance)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "http://banana.com/detail",
            "p2pEndpoint": "123.213.123.123:7100"
        }
        tx = self.create_register_prep_tx(wallet, params)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(False, tx_result['status'])

        response = self.get_prep(wallet)
        self.assertTrue(response['message'].startswith('P-Rep not found'))

    def test_3_register_one_prep(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        wallet = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1,
                                         wallet.get_address(),
                                         init_balance)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "http://banana.com/detail",
            "publicKey": f"0x{wallet.bytes_public_key.hex()}",
            "p2pEndpoint": "123.213.123.123:7100"
        }
        tx = self.create_register_prep_tx(wallet, params)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])

        # set prep on pre-voting
        params1 = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "http://banana.com/detail",
            "p2pEndpoint": "123.213.123.123:7100"
        }
        tx = self.create_set_prep_tx(wallet, set_data=params1)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])

        response = self.get_prep(wallet)
        prep_data = response['registration']
        self.assertEqual(prep_data['name'], params1['name'])
        self.assertEqual(prep_data['email'], params1['email'])
        self.assertEqual(prep_data['website'], params1['website'])
        self.assertEqual(prep_data['details'], params1['details'])
        self.assertEqual(prep_data['p2pEndpoint'], params1['p2pEndpoint'])

        # set irep on pre-voting
        irep = 40000
        params = {
            "name": "apple node2",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "http://banana.com/detail",
            "p2pEndpoint": "123.213.123.123:7100",
        }
        tx = self.create_set_prep_tx(wallet, irep, params)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(False, tx_result['status'])

        response = self.get_prep(wallet)
        prep_data = response['registration']
        self.assertEqual(prep_data['name'], params1['name'])
        self.assertEqual(prep_data['email'], params1['email'])
        self.assertEqual(prep_data['website'], params1['website'])
        self.assertEqual(prep_data['details'], params1['details'])
        self.assertEqual(prep_data['p2pEndpoint'], params1['p2pEndpoint'])
        self.assertNotEqual(prep_data['irep'], hex(irep))

    def test_4_register_100_preps_and_check_total_delegated(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        wallets = [KeyWallet.create() for _ in range(100)]
        tx_list = self.distribute_icx(self._test1,
                                      wallets,
                                      init_balance)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])

        tx_list = []
        for i, wallet in enumerate(wallets):
            params = {
                "name": f"banana node{i}",
                "email": f"banana@banana{i}.com",
                "website": f"https://banana{i}.com",
                "details": f"http://banana.com/detail{i}",
                "publicKey": f"0x{wallet.bytes_public_key.hex()}",
                "p2pEndpoint": f"3.213.123.123:71{i}"
            }
            tx = self.create_register_prep_tx(wallets[i], params)
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])

        # check total delegated
        # distribute icx
        delegators = [KeyWallet.create() for _ in range(10)]
        tx_list = self.distribute_icx(self._test1, delegators, init_balance)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])

        # stake
        tx_list = []
        for index, key_wallet in enumerate(delegators):
            tx = self.create_set_stake_tx(key_wallet, 1 * ICX_FACTOR)
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])

        # delegate
        delegate_info_list = []
        delegate_amount = [100 - i for i in range(100)]
        for index, key_wallet in enumerate(wallets):
            delegate_info = (key_wallet, 100-index)
            delegate_info_list.append(delegate_info)

        tx_list = []
        for index, key_wallet in enumerate(delegators):
            tx = self.create_set_delegation_tx(key_wallet,
                                               delegate_info_list[index * 10: index * 10 + 10])
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])

        # check total Delegated 50 to 70
        response_50_to_70 = self.get_prep_list(50, 70)
