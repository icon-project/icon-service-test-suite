from typing import List, Tuple

from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.type_converter_templates import ConstantKeys
from iconservice.icon_constant import REV_IISS

from test_suite.json_rpc_api.base import Base, ICX_FACTOR, Account


class TestPRepScenario(Base):
    def test_scenario(self):
        test1_account = Account(self._test1)
        self._wallet_array = [Account(KeyWallet.create()) for _ in range(212)]
        _PREPS = self._wallet_array[:200]
        _SUB_PREPS = self._wallet_array[:100]
        _ICONIST = self._wallet_array[202:]
        preps_init_balance_list = []
        DIVIDEND = 10_000 * ICX_FACTOR
        STAKE_VALUE = 100 * ICX_FACTOR

        # 1 set revision to REV_IISS
        print('start #1 set revision to REV_IISS')
        tx = self.create_set_revision_tx(test1_account, REV_IISS)
        tx_hashes = self.process_transaction_bulk_without_txresult([tx], self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])
            test1_account.balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # 2 transfer to PREPS and ICONists
        print('start #2 transfer to accounts')
        self.distribute_icx(self._wallet_array, DIVIDEND)

        # 3 check balance of accounts
        print('start #3 check balance')
        for account in self._wallet_array:
            balance = self.icon_service.get_balance(account.wallet.address)
            self.assertEqual(balance, DIVIDEND)
            preps_init_balance_list.append(balance)

        # 4 register p-reps
        print('start #4 register preps')
        self.register_prep(_PREPS)

        # 5 set p-reps except irep
        print('start #5 set preps')
        tx_list = []
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
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            account = _PREPS[i]
            account.balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # 6 get preps and check set data properly
        print('start #6 check set data properly')
        for index, account in enumerate(_PREPS):
            prep = self.get_prep(account)
            self.assertEqual(expected_prep_data[index][ConstantKeys.NAME], prep[ConstantKeys.NAME])
            self.assertEqual(expected_prep_data[index][ConstantKeys.EMAIL], prep[ConstantKeys.EMAIL])
            self.assertEqual(expected_prep_data[index][ConstantKeys.WEBSITE], prep[ConstantKeys.WEBSITE])
            self.assertEqual(expected_prep_data[index][ConstantKeys.DETAILS], prep[ConstantKeys.DETAILS])
            self.assertEqual(expected_prep_data[index][ConstantKeys.P2P_ENDPOINT],
                             prep[ConstantKeys.P2P_ENDPOINT])

        # 7-1 ICONist stake 100ICX
        print('start #7 ICONISt stake 100icx')
        self.set_stake(_ICONIST, STAKE_VALUE)
        # 7-2 check balance and stake
        for i, account in enumerate(_ICONIST):
            balance = self.icon_service.get_balance(account.wallet.address)
            stake = int(self.get_stake(account.wallet.address)['stake'], 16)
            self.assertEqual(STAKE_VALUE, stake)
            self.assertEqual(_ICONIST[i].balance - STAKE_VALUE, balance)

        # 8-1 Add empty blocks
        print('start #8')
        self._make_blocks_to_end_calculation()

        # 8-2 check I-Scores
        for account in self._wallet_array:
            iscore_info = self.query_iscore(account)
            self.assertEqual(iscore_info['iscore'], hex(0))

        # 9 delegate
        print('start #9 delegate')
        tx_list = []
        delegate_info: List[Tuple['Account', int]] = \
            [(prep, (index+1) * 10 * ICX_FACTOR) for index, prep in enumerate(_PREPS[:len(_ICONIST)])]
        for index, account in enumerate(_ICONIST):
            tx = self.create_set_delegation_tx(account, [delegate_info[index]])
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            _ICONIST[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # 9-2 check rank and delegation
        get_preps_response = self.get_prep_list()
        preps_info = get_preps_response['preps']
        for index, account in enumerate(reversed(_PREPS[:len(_ICONIST)])):
            self.assertEqual(preps_info[index]['address'], account.wallet.address)
            self.assertEqual(int(preps_info[index]['delegated'], 16), delegate_info[len(_ICONIST) - index - 1][1])

        # 10 revoke delegation
        print('start #10 revoke delegation')
        tx_list = []
        for account in _ICONIST:
            tx = self.create_set_delegation_tx(account, [])
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            _ICONIST[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        for index, account in enumerate(_PREPS[:len(_ICONIST)]):
            prep_info = self.get_prep(account)
            prep_delegation = prep_info['delegated']
            self.assertEqual(int(prep_delegation, 16), 0)

        # 11 multiple delegation
        print('start #11 multiple delegation')
        delegate_info: List[Tuple['Account', int]] = \
            [(prep, ((index+10) // 10) * ICX_FACTOR) for index, prep in enumerate(_SUB_PREPS)]
        delegate_tx_list = []
        for index, account in enumerate(_ICONIST):
            tx = self.create_set_delegation_tx(account, delegate_info[index*10:index*10+10])
            delegate_tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(delegate_tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            _ICONIST[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        for index, account in enumerate(reversed(_SUB_PREPS)):
            prep_info = self.get_prep(account)
            prep_delegation = prep_info['delegated']
            self.assertEqual(int(prep_delegation, 16), delegate_info[len(_SUB_PREPS) - index - 1][1])

        # 12 11 delegation
        print('start #12 11delegation')
        delegate_info: List[Tuple['Account', int]] = \
            [(prep, ((index+10) // 10) * ICX_FACTOR) for index, prep in enumerate(self._wallet_array[100:201])]
        delegate_tx_list = []
        for index, account in enumerate(_ICONIST):
            tx = self.create_set_delegation_tx(account, delegate_info[index*10:index*10+11])
            delegate_tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(delegate_tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 0)
            _ICONIST[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        get_preps_response = self.get_prep_list()
        preps_info = get_preps_response['preps']
        for index, account in enumerate(reversed(_SUB_PREPS)):
            self.assertEqual(int(preps_info[index]['delegated'], 16), delegate_info[len(_SUB_PREPS) - index - 1][1])

        # 13 get main preps
        print('start #13 get main_preps')
        response = self.get_main_prep_list()
        main_preps = response['preps']
        self.assertFalse(main_preps)

        # 14 get sub preps
        print('start #14 get sub_preps')
        response = self.get_sub_prep_list()
        _SUB_PREPS = response['preps']
        self.assertFalse(_SUB_PREPS)

        # 15 unregister preps 0-9
        print('start #15 unregister preps 0-9')
        unregister_tx_list = []
        for i in range(10):
            tx = self.create_unregister_prep_tx(_PREPS[i])
            unregister_tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(unregister_tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            _PREPS[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # 16 get preps 0-9 (changed. error not raised)
        # print('start #16')
        # for i in range(10):
        #     response = self.get_prep(_PREPS[i])
        #     self.assertTrue(response['message'].startswith('P-Rep not found: '))

        # 17 register 0-9 preps again
        print('start #17 register 0-9 preps again')
        tx_list = []
        for i in range(10):
            tx = self.create_register_prep_tx(_PREPS[i])
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 0)
            _PREPS[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # 18 set prep 0-9 preps
        print('start #18 set prep 0-9')
        tx_list = []
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
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 0)
            _PREPS[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # 19 register preps 10-19 again
        print('start #19 register preps 10-19 again')
        tx_list = []
        for i in range(10, 20):
            tx = self.create_register_prep_tx(_PREPS[i])
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 0)
            _PREPS[i+10].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # 20 query ICONist-9 i-score
        self._make_blocks_to_end_calculation()
        self._make_blocks_to_end_calculation()
        print('start #20 query ICONIST9 iscore')
        response = self.query_iscore(_ICONIST[9])
        iscore1 = response['iscore']
        self.assertNotEqual(iscore1, hex(0))

        # 21 claim ICONist-9 i-score
        print('start #21 claim ICONIST9 iscore')
        self.claim_iscore([_ICONIST[9]])

        # 22 query ICONist-9 i-score
        print('start #22 query ICONIST9 iscore')
        response = self.query_iscore(_ICONIST[9])
        iscore2 = response['iscore']
        self.assertNotEqual(iscore2, iscore1)

        # 23 pass
        print('pass #23')

        # 24 self delegation
        print('start #24 prep99 set delegation 1000icx to PREP99')
        tx_list = []
        tx = self.create_set_stake_tx(_PREPS[99], 1000 * ICX_FACTOR)
        tx_list.append(tx)
        tx = self.create_set_delegation_tx(_PREPS[99], [(_PREPS[99], 1000 * ICX_FACTOR)])
        tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            _PREPS[99].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        response = self.get_prep_list()
        preps_info = response['preps']
        self.assertEqual(preps_info[0]['address'], _PREPS[99].wallet.address)

        print("# start refund")
        self.refund_icx(self._wallet_array)
        # 25 reload
