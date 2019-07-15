from typing import List

from iconsdk.builder.transaction_builder import TransactionBuilder
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from test_suite.json_rpc_api.base import Base, ICX_FACTOR, PREP_REGISTER_COST_ICX


class TestPRep(Base):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    def _distribute_icx(self, addresses: List['KeyWallet']):
        tx_list = []
        for key_wallet in addresses:
            transaction = TransactionBuilder(). \
                value((PREP_REGISTER_COST_ICX+1)*ICX_FACTOR). \
                from_(self._test1.get_address()). \
                to(key_wallet.get_address()). \
                nid(3). \
                nonce(1). \
                step_limit(1000000). \
                version(3). \
                build()
            signed_transaction = SignedTransaction(transaction, self._test1)
            tx_list.append(signed_transaction)
        return tx_list

    def test_1_register_one_prep_invalid_case1(self):
        account = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1, account.get_address(), (PREP_REGISTER_COST_ICX+1)*ICX_FACTOR)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "http://banana.com/detail",
            "publicKey": f"0x{account.bytes_public_key.hex()}"
        }
        tx = self.create_register_prep_tx(account, params, step_limit=10000000)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

        response = self.get_prep(account)
        self.assertTrue(response['message'].startswith('P-Rep not found'))

    def test_2_register_one_prep_invalid_case2(self):
        account = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1, account.get_address(), (PREP_REGISTER_COST_ICX+1)*ICX_FACTOR)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "http://banana.com/detail",
            "p2pEndpoint": "123.213.123.123:7100"
        }
        tx = self.create_register_prep_tx(account, params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

        response = self.get_prep(account)
        self.assertTrue(response['message'].startswith('P-Rep not found'))

    def test_3_register_one_prep(self):
        account = KeyWallet.create()
        tx = self.create_transfer_icx_tx(self._test1, account.get_address(), (PREP_REGISTER_COST_ICX+1)*ICX_FACTOR)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)
        params = {
            "name": "banana node",
            "email": "banana@banana.com",
            "website": "https://banana.com",
            "details": "http://banana.com/detail",
            "publicKey": f"0x{account.bytes_public_key.hex()}",
            "p2pEndpoint": "123.213.123.123:7100"
        }
        tx = self.create_register_prep_tx(account, params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        # set prep on pre-voting
        params1 = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "http://banana.com/detail",
            "p2pEndpoint": "123.213.123.123:7100"
        }
        tx = self.create_set_prep_tx(account, set_data=params1)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        response = self.get_prep(account)
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
        tx = self.create_set_prep_tx(account, irep, params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

        response = self.get_prep(account)
        prep_data = response['registration']
        self.assertEqual(prep_data['name'], params1['name'])
        self.assertEqual(prep_data['email'], params1['email'])
        self.assertEqual(prep_data['website'], params1['website'])
        self.assertEqual(prep_data['details'], params1['details'])
        self.assertEqual(prep_data['p2pEndpoint'], params1['p2pEndpoint'])
        self.assertNotEqual(prep_data['irep'], hex(irep))

    def test_4_register_100_preps_and_check_total_delegated(self):
        accounts = [KeyWallet.create() for _ in range(100)]
        tx_list = self._distribute_icx(accounts)
        self.process_transaction_bulk(tx_list, self.icon_service)
        tx_list = []
        for i, account in enumerate(accounts):
            params = {
                "name": f"banana node{i}",
                "email": f"banana@banana{i}.com",
                "website": f"https://banana{i}.com",
                "details": f"http://banana.com/detail{i}",
                "publicKey": f"0x{account.bytes_public_key.hex()}",
                "p2pEndpoint": f"3.213.123.123:71{i}"
            }
            tx = self.create_register_prep_tx(accounts[i], params, step_limit=10000000)
            tx_list.append(tx)

        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)

        for result in tx_results:
            self.assertEqual(result['status'], 1)

        # check total delegated
        # distribute icx
        delegators = [KeyWallet.create() for _ in range(10)]
        tx_list = self._distribute_icx(delegators)
        self.process_transaction_bulk(tx_list, self.icon_service)

        # stake
        stake_tx_list = []
        for index, key_wallet in enumerate(delegators):
            tx = self.create_set_stake_tx(key_wallet, 10**18)
            stake_tx_list.append(tx)

        self.process_transaction_bulk(stake_tx_list, self.icon_service)

        # delegate
        delegate_info_list = []
        delegate_amount = [100 - i for i in range(100)]
        for index, key_wallet in enumerate(accounts):
            delegate_info = (key_wallet, 100-index)
            delegate_info_list.append(delegate_info)

        delegate_tx_list = []
        for index, key_wallet in enumerate(delegators):
            tx = self.create_set_delegation_tx(key_wallet, delegate_info_list[index*10:index*10+10],
                                               step_limit=10000000)
            delegate_tx_list.append(tx)
        self.process_transaction_bulk(delegate_tx_list, self.icon_service)

        # check total Delegated 50 to 70
        response_50_to_70 = self.get_prep_list(50, 70)
