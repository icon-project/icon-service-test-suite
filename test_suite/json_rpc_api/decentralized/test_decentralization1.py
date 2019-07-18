import os

from iconsdk.wallet.wallet import KeyWallet
from iconservice.icon_constant import REV_DECENTRALIZATION

from test_suite.json_rpc_api.base import ICX_FACTOR
from test_suite.json_rpc_api.decentralized.decentralizationBase import DecentralizationBase

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestDecentralization1(DecentralizationBase):

    def test_1_decentralization(self):
        wallet_array = [KeyWallet.create() for _ in range(40)]
        # distribute icx
        iconists = wallet_array[-3:]
        preps = wallet_array[:30]
        total_supply = self.icon_service.get_total_supply()

        minimum_delegate_amount = total_supply * 3 // 1000
        distribute_icx_tx_results1 = self.distribute_icx(self._test1, iconists, int(minimum_delegate_amount * 11.5))
        for tx_result in distribute_icx_tx_results1:
            self.assertEqual(tx_result['status'], 1)
        distribute_icx_tx_results2 = self.distribute_icx(self._test1, preps, 2010*ICX_FACTOR)
        for tx_result in distribute_icx_tx_results2:
            self.assertEqual(tx_result['status'], 1)

        # stake
        tx_results = self.stake_bulk(iconists, minimum_delegate_amount*11)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)

        # delegate
        delegate_tx_result1 = self.delegate(iconists[0], preps[:10], minimum_delegate_amount + 100, -1)
        delegate_tx_result2 = self.delegate(iconists[1], preps[10:20], minimum_delegate_amount + 50, -1)
        delegate_tx_result3 = self.delegate(iconists[2], preps[20:], minimum_delegate_amount + 10, -1)
        self.assertEqual(delegate_tx_result1['status'], 1)
        self.assertEqual(delegate_tx_result2['status'], 1)
        self.assertEqual(delegate_tx_result3['status'], 1)

        # register preps
        tx_results = self.register_prep_bulk(preps)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)

        # set revision to REV_DECENTRALIZATION
        set_revision_tx = self.create_set_revision_tx(self._test1, REV_DECENTRALIZATION)
        tx_result = self.process_transaction(set_revision_tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        response = self.get_main_prep_list()
        self.assertTrue(response['preps'])

        # delegate revoke
        revoke_tx1 = self.delegate(iconists[0], preps[:10], 0)
        revoke_tx2 = self.delegate(iconists[1], preps[10:20], 0)
        revoke_tx3 = self.delegate(iconists[2], preps[20:], 0)
        self.assertEqual(revoke_tx1['status'], 1)
        self.assertEqual(revoke_tx2['status'], 1)
        self.assertEqual(revoke_tx3['status'], 1)

        # network decentralized

        # # normal account try to set prep
        # params = {
        #     "name": "apple node",
        #     "email": "apple@banana.com",
        #     "website": "https://apple.com",
        #     "details": "detail",
        #     "p2pEndPoint": "target://123.213.123.123:7100",
        # }
        # tx = self.create_set_prep_tx(iconists[0], set_data=params)
        # tx_result = self.process_transaction(tx, self.icon_service)
        # self.assertEqual(tx_result['status'], 0)
        #
        # # unregistered prep try to set prep
        # tx = self.create_unregister_prep_tx(preps[3])
        # tx_result = self.process_transaction(tx, self.icon_service)
        # self.assertEqual(tx_result['status'], 1)
        #
        # params = {
        #     "name": "apple node",
        #     "email": "apple@banana.com",
        #     "website": "https://apple.com",
        #     "details": "detail",
        #     "p2pEndPoint": "target://123.213.123.123:7100",
        # }
        #
        # tx = self.create_set_prep_tx(preps[3], set_data=params)
        # tx_result = self.process_transaction(tx, self.icon_service)
        # self.assertEqual(tx_result['status'], 0)
        #
        # unregister_tx_list = [self.create_unregister_prep_tx(prep) for prep in preps[:3]]
        # self.process_transaction_bulk(unregister_tx_list, self.icon_service)
        # self._make_blocks_to_end_calculation()
        #
        # response = self.process_call(get_main_preps_request, self.icon_service)
        # prep_info_list = response['preps']
        # prep_list = list(map(lambda res: res['address'], prep_info_list))
        #
        # self.assertNotIn(preps[0].get_address(), prep_list)
        # self.assertNotIn(preps[1].get_address(), prep_list)
        # self.assertNotIn(preps[2].get_address(), prep_list)
        # self.assertNotIn(preps[3].get_address(), prep_list)
        # self.assertIn(preps[25].get_address(), prep_list)
        # self.assertIn(preps[24].get_address(), prep_list)
        # self.assertIn(preps[23].get_address(), prep_list)
        # self.assertIn(preps[22].get_address(), prep_list)
        #
        # # set irep twice in term
        # prep = preps[4]
        # set_irep_tx = self.create_set_prep_tx(prep, IISS_INITIAL_IREP * 9 // 10)
        # tx_result = self.process_transaction(set_irep_tx, self.icon_service)
        # self.assertEqual(tx_result['status'], 1)
        #
        # set_irep_tx = self.create_set_prep_tx(prep, IISS_INITIAL_IREP * 9 // 10)
        # tx_result = self.process_transaction(set_irep_tx, self.icon_service)
        # self.assertEqual(tx_result['status'], 0)
