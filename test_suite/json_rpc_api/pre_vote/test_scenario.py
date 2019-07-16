from typing import List, Tuple

from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.type_converter_templates import ConstantKeys
from iconservice.icon_constant import REV_IISS

from test_suite.json_rpc_api.base import Base

ICX_FACTOR = 10 ** 18


class TestPRepScenario(Base):
    def test_scenario(self):
        self._wallet_array = [KeyWallet.create() for _ in range(212)]
        _PREPS = self._wallet_array[:200]
        _SUB_PREPS = self._wallet_array[:100]
        _ICONIST = self._wallet_array[202:]
        preps_init_balance_list = []
        iconist_init_balance_list = []
        DIVIDEND = 10_000 * ICX_FACTOR
        STAKE_VALUE = 100 * ICX_FACTOR

        # 1 set revision to REV_IISS
        print('start #1')
        set_rev_tx = self.create_set_revision_tx(self._test1, REV_IISS)
        set_rev_tx_result = self.process_transaction(set_rev_tx, self.icon_service)
        self.assertEqual(set_rev_tx_result['status'], 1)

        # 2 transfer to PREPS and ICONists
        print('start #2')
        transfer_tx_list = []
        for account in self._wallet_array:
            tx = self.create_transfer_icx_tx(self._test1, account, DIVIDEND)
            transfer_tx_list.append(tx)
        self.process_transaction_bulk(transfer_tx_list, self.icon_service)

        # 3 check balance of accounts
        print('start #3')
        for account in _PREPS:
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(balance, DIVIDEND)
            preps_init_balance_list.append(balance)

        for account in _ICONIST:
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(balance, DIVIDEND)
            iconist_init_balance_list.append(balance)

        # 4 register p-reps
        print('start #4')
        register_tx_list = []
        for account in _PREPS:
            tx = self.create_register_prep_tx(account)
            register_tx_list.append(tx)
        register_tx_results = self.process_transaction_bulk(register_tx_list, self.icon_service)
        for tx_result in register_tx_results:
            self.assertEqual(tx_result['status'], 1)

        # 5 set p-reps except irep
        print('start #5')
        set_prep_tx_list = []
        expected_prep_data = []
        for index, account in enumerate(_PREPS):
            name = f"prep{index}"
            set_prep_data = {
                ConstantKeys.NAME: name,
                ConstantKeys.EMAIL: f"prep{name}@example.com",
                ConstantKeys.WEBSITE: f"https://prep{name}.example.com",
                ConstantKeys.DETAILS: f"https://prep{name}.example.com/details",
                ConstantKeys.P2P_ENDPOINT: f"prep{name}.example.com:7100"
            }
            expected_prep_data.append(set_prep_data)
            tx = self.create_set_prep_tx(account, set_data=set_prep_data)
            set_prep_tx_list.append(tx)
        self.process_transaction_bulk(set_prep_tx_list, self.icon_service)

        # 6 get preps and check set data properly
        print('start #6')
        for index, account in enumerate(_PREPS):
            prep = self.get_prep(account)
            prep_info = prep['registration']
            self.assertEqual(expected_prep_data[index][ConstantKeys.NAME], prep_info[ConstantKeys.NAME])
            self.assertEqual(expected_prep_data[index][ConstantKeys.EMAIL], prep_info[ConstantKeys.EMAIL])
            self.assertEqual(expected_prep_data[index][ConstantKeys.WEBSITE], prep_info[ConstantKeys.WEBSITE])
            self.assertEqual(expected_prep_data[index][ConstantKeys.DETAILS], prep_info[ConstantKeys.DETAILS])
            self.assertEqual(expected_prep_data[index][ConstantKeys.P2P_ENDPOINT],
                             prep_info[ConstantKeys.P2P_ENDPOINT])

        # 7-1 ICONist stake 100ICX
        print('start #7')
        stake_tx_list = []
        stake_fee_list = []
        for account in _ICONIST:
            tx = self.create_set_stake_tx(account, STAKE_VALUE)
            stake_tx_list.append(tx)
        stake_tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)

        for tx_result in stake_tx_results:
            fee = tx_result['stepUsed'] * tx_result['stepPrice']
            stake_fee_list.append(fee)

        # 7-2 check balance and stake
        for index, account in enumerate(_ICONIST):
            balance = self.icon_service.get_balance(account.get_address())
            self.assertEqual(iconist_init_balance_list[index] - stake_fee_list[index] - STAKE_VALUE, balance)

        # 8-1 Add empty blocks
        print('start #8')
        self._make_blocks_to_next_calculation()
        self._make_blocks_to_next_calculation()

        # 8-2 check I-Scores
        for account in self._wallet_array:
            iscore_info = self.query_iscore(account)
            self.assertEqual(iscore_info['iscore'], hex(0))

        # 9 delegate
        print('start #9')
        delegate_tx_list = []
        delegate_info: List[Tuple['KeyWallet', int]] = \
            [(prep, (index+1) * 10 * ICX_FACTOR) for index, prep in enumerate(_PREPS[:len(_ICONIST)])]
        for index, account in enumerate(_ICONIST):
            tx = self.create_set_delegation_tx(account, [delegate_info[index]])
            delegate_tx_list.append(tx)
        delegate_tx_results = self.process_transaction_bulk(delegate_tx_list, self.icon_service)

        # 9-2 check rank and delegation
        get_preps_response = self.get_prep_list()
        preps_info = get_preps_response['preps']
        for index, account in enumerate(reversed(_PREPS[:len(_ICONIST)])):
            self.assertEqual(preps_info[index]['address'], account.get_address())
            self.assertEqual(int(preps_info[index]['delegated'], 16), delegate_info[len(_ICONIST) - index - 1][1])

        # 10 revoke delegation
        print('start #10')
        delegate_tx_list = []
        for account in _ICONIST:
            tx = self.create_set_delegation_tx(account, [])
            delegate_tx_list.append(tx)
        self.process_transaction_bulk(delegate_tx_list, self.icon_service)

        for index, account in enumerate(_PREPS[:len(_ICONIST)]):
            prep_info = self.get_prep(account)
            prep_delegation = prep_info['delegation']['delegated']
            self.assertEqual(int(prep_delegation, 16), 0)

        # 11 multiple delegation
        print('start #11')
        delegate_info: List[Tuple['KeyWallet', int]] = \
            [(prep, ((index+10) // 10) * ICX_FACTOR) for index, prep in enumerate(_SUB_PREPS)]
        delegate_tx_list = []
        for index, account in enumerate(_ICONIST):
            tx = self.create_set_delegation_tx(account, delegate_info[index*10:index*10+10])
            delegate_tx_list.append(tx)
        delegate_tx_results = self.process_transaction_bulk(delegate_tx_list, self.icon_service)

        for index, account in enumerate(reversed(_SUB_PREPS)):
            prep_info = self.get_prep(account)
            prep_delegation = prep_info['delegation']['delegated']
            self.assertEqual(int(prep_delegation, 16), delegate_info[len(_SUB_PREPS) - index - 1][1])

        # 12 11 delegation
        print('start #12')
        delegate_info: List[Tuple['KeyWallet', int]] = \
            [(prep, ((index+10) // 10) * ICX_FACTOR) for index, prep in enumerate(self._wallet_array[100:201])]
        delegate_tx_list = []
        for index, account in enumerate(_ICONIST):
            tx = self.create_set_delegation_tx(account, delegate_info[index*10:index*10+11])
            delegate_tx_list.append(tx)
        delegate_tx_results = self.process_transaction_bulk(delegate_tx_list, self.icon_service)

        for tx_result in delegate_tx_results:
            self.assertEqual(tx_result['status'], 0)

        get_preps_response = self.get_prep_list()
        preps_info = get_preps_response['preps']
        for index, account in enumerate(reversed(_SUB_PREPS)):
            self.assertEqual(int(preps_info[index]['delegated'], 16), delegate_info[len(_SUB_PREPS) - index - 1][1])

        # 13 get main preps
        print('start #13')
        response = self.get_main_prep_list()
        main_preps = response['preps']
        self.assertFalse(main_preps)

        # 14 get sub preps
        print('start #14')
        response = self.get_sub_prep_list()
        _SUB_PREPS = response['preps']
        self.assertFalse(_SUB_PREPS)

        # 15 unregister preps 0-9
        print('start #15')
        unregister_tx_list = []
        for i in range(10):
            tx = self.create_unregister_prep_tx(_PREPS[i])
            unregister_tx_list.append(tx)
        tx_results = self.process_transaction_bulk(unregister_tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertEqual(tx_result['status'], 1)
        # preps = self.get_prep_list()
        # self.assertEqual(len(preps['preps']), len(_PREPS) - 10)

        # 16 get preps 0-9 (changed. error not raised)
        # print('start #16')
        # for i in range(10):
        #     response = self.get_prep(_PREPS[i])
        #     self.assertTrue(response['message'].startswith('P-Rep not found: '))

        # 17 register 0-9 preps again
        print('start #17')
        register_tx_list = []
        for i in range(10):
            tx = self.create_register_prep_tx(_PREPS[i])
            register_tx_list.append(tx)
        register_tx_results = self.process_transaction_bulk(register_tx_list, self.icon_service)
        for tx_result in register_tx_results:
            print(tx_result)
            self.assertEqual(tx_result['status'], 0)

        # 18 set prep 0-9 preps
        print('start #18')
        set_prep_tx_list = []
        for index, account in enumerate(_PREPS[:10]):
            name = f"node{index}"
            set_prep_data = {
                ConstantKeys.NAME: name,
                ConstantKeys.EMAIL: f"node{name}@example.com",
                ConstantKeys.WEBSITE: f"https://node{name}.example.com",
                ConstantKeys.DETAILS: f"https://node{name}.example.com/details",
                ConstantKeys.P2P_ENDPOINT: f"node{name}.example.com:7100"
            }
            tx = self.create_set_prep_tx(account, set_data=set_prep_data)
            set_prep_tx_list.append(tx)
        set_prep_tx_results = self.process_transaction_bulk(set_prep_tx_list, self.icon_service)
        for tx_result in set_prep_tx_results:
            self.assertEqual(tx_result['status'], 0)

        # 19 register preps 10-19 again
        print('start #19')
        register_prep_tx_list = []
        for i in range(10, 19):
            tx = self.create_register_prep_tx(_PREPS[i])
            register_prep_tx_list.append(tx)
        register_prep_tx_results = self.process_transaction_bulk(register_prep_tx_list, self.icon_service)
        for tx_result in register_prep_tx_results:
            self.assertEqual(tx_result['status'], 0)

        # 20 query ICONist-9 i-score
        self._make_blocks_to_next_calculation()
        print('start #20')
        response = self.query_iscore(_ICONIST[9])
        iscore1 = response['iscore']
        self.assertNotEqual(iscore1, hex(0))

        # 21 claim ICONist-9 i-score
        print('start #21')
        claim_tx = self.create_claim_iscore_tx(_ICONIST[9])
        tx_result = self.process_transaction(claim_tx, self.icon_service)
        self.assertEqual(tx_result['status'], 1)

        # 22 query ICONist-9 i-score
        print('start #22')
        response = self.query_iscore(_ICONIST[9])
        iscore2 = response['iscore']
        self.assertNotEqual(iscore2, iscore1)

        # 23 pass
        print('pass #23')

        # 24 self delegation
        print('start #24')
        stake_tx = self.create_set_stake_tx(_PREPS[99], 1000 * ICX_FACTOR)
        self.process_transaction(stake_tx, self.icon_service)
        delegate_tx = self.create_set_delegation_tx(_PREPS[99], [(_PREPS[99], 1000 * ICX_FACTOR)])
        self.process_transaction(delegate_tx, self.icon_service)

        response = self.get_prep_list()
        preps_info = response['preps']
        self.assertEqual(preps_info[0]['address'], _PREPS[99].get_address())
        # 25 reload
