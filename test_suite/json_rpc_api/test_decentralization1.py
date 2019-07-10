import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.wallet.wallet import KeyWallet
from iconservice.icon_constant import REV_DECENTRALIZATION, IISS_INITIAL_IREP

from .base import Base, SYSTEM_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestDecentralization1(Base):

    def test_1_decentralization(self):
        wallet_array = [KeyWallet.create() for _ in range(40)]
        # distribute icx
        iconists = wallet_array[-3:]
        preps = wallet_array[:30]
        total_supply = self.icon_service.get_total_supply()

        minimum_delegate_amount = total_supply * 3 // 1000
        distribute_tx_list = [self.create_transfer_icx_tx(self._test1, wallet, minimum_delegate_amount * 115 // 10)
                              for wallet in iconists]
        distribute_tx_list2 = [self.create_transfer_icx_tx(self._test1, wallet, 2010 * 10 ** 18)
                               for wallet in preps]
        tx_results = self.process_transaction_bulk(distribute_tx_list + distribute_tx_list2, self.icon_service)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)

        # stake
        stake_tx_list = [self.create_set_stake_tx(wallet, minimum_delegate_amount * 11) for wallet in iconists]
        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)

        # delegate
        delegation_data1 = [(wallet, minimum_delegate_amount + 100 - index) for index, wallet in enumerate(preps[:10])]
        delegation_tx1 = self.create_set_delegation_tx(wallet_array[-3], delegation_data1)
        delegation_data2 = [(wallet, minimum_delegate_amount + 50 - index) for index, wallet in enumerate(preps[10:20])]
        delegation_tx2 = self.create_set_delegation_tx(wallet_array[-2], delegation_data2)
        delegation_data3 = [(wallet, minimum_delegate_amount + 10 - index) for index, wallet in enumerate(preps[20:26])]
        delegation_tx3 = self.create_set_delegation_tx(wallet_array[-1], delegation_data3)
        delegation_data = delegation_data1 + delegation_data2 + delegation_data3
        tx_results = self.process_transaction_bulk([delegation_tx1, delegation_tx2, delegation_tx3], self.icon_service)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)

        # register preps
        reg_tx_list = []
        for i, wallet in enumerate(preps):
            params = {
                "name": f"banana node{i}",
                "email": f"banana@banana{i}.com",
                "website": f"https://banana{i}.com",
                "details": f"detail{i}",
                "publicKey": f"0x{wallet.bytes_public_key.hex()}",
                "p2pEndPoint": f"{i}.213.123.123:7100"
            }
            tx = self.create_register_prep_tx(wallet, params)
            reg_tx_list.append(tx)
        tx_results = self.process_transaction_bulk(reg_tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)

        # set revision to REV_DECENTRALIZATION
        set_revision_tx = self.create_set_revision_tx(self._test1, REV_DECENTRALIZATION)
        tx_result = self.process_transaction(set_revision_tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        get_main_preps_request = CallBuilder().from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getMainPRepList") \
            .build()
        response = self.process_call(get_main_preps_request, self.icon_service)
        self.assertTrue(response['preps'])

        # network decentralized

        # normal account try to set prep
        params = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100",
        }
        tx = self.create_set_prep_tx(iconists[0], set_data=params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

        # unregistered prep try to set prep
        tx = self.create_unregister_prep_tx(preps[3])
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        params = {
            "name": "apple node",
            "email": "apple@banana.com",
            "website": "https://apple.com",
            "details": "detail",
            "p2pEndPoint": "target://123.213.123.123:7100",
        }

        tx = self.create_set_prep_tx(preps[3], set_data=params)
        tx_result = self.process_transaction(tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)

        unregister_tx_list = [self.create_unregister_prep_tx(prep) for prep in preps[:3]]
        self.process_transaction_bulk(unregister_tx_list, self.icon_service)
        self._make_blocks_to_next_calculation()

        response = self.process_call(get_main_preps_request, self.icon_service)
        prep_info_list = response['preps']
        prep_list = list(map(lambda res: res['address'], prep_info_list))

        self.assertNotIn(preps[0].get_address(), prep_list)
        self.assertNotIn(preps[1].get_address(), prep_list)
        self.assertNotIn(preps[2].get_address(), prep_list)
        self.assertNotIn(preps[3].get_address(), prep_list)
        self.assertIn(preps[25].get_address(), prep_list)
        self.assertIn(preps[24].get_address(), prep_list)
        self.assertIn(preps[23].get_address(), prep_list)
        self.assertIn(preps[22].get_address(), prep_list)

        # set irep twice in term
        prep = preps[4]
        set_irep_tx = self.create_set_prep_tx(prep, IISS_INITIAL_IREP * 9 // 10)
        tx_result = self.process_transaction(set_irep_tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        set_irep_tx = self.create_set_prep_tx(prep, IISS_INITIAL_IREP * 9 // 10)
        tx_result = self.process_transaction(set_irep_tx, self.icon_service)
        self.assertEqual(tx_result['status'], 0)
