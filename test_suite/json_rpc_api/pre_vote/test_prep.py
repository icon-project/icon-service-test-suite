import copy
from typing import List, TYPE_CHECKING, Tuple

from iconservice.base.type_converter_templates import ConstantKeys

from test_suite.json_rpc_api.base import Base, ICX_FACTOR, PREP_REGISTER_COST_ICX

if TYPE_CHECKING:
    from ..base import Account


class TestPRep(Base):

    def test_1_register_prep(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        account_count: int = 1
        accounts: List['Account'] = self.create_accounts(account_count)
        account = accounts[0]

        # create
        self.distribute_icx(accounts, init_balance)

        keys = [ConstantKeys.P2P_ENDPOINT, ConstantKeys.PUBLIC_KEY, ConstantKeys.WEBSITE, ConstantKeys.DETAILS,
                ConstantKeys.EMAIL, ConstantKeys.NAME, ConstantKeys.CITY, ConstantKeys.COUNTRY]
        register_data = self._create_register_prep_params(account)

        # register prep with invalid data
        for key in keys:
            data = copy.deepcopy(register_data)
            data[key] = ''
            tx = self.create_register_prep_tx(account, data)
            tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
            self.process_confirm_block_tx(self.icon_service)
            tx_results = self.get_txresults(self.icon_service, tx_hashes)
            for i, tx_result in enumerate(tx_results):
                self.assertEqual(tx_result['status'], 0)
                account.balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # register prep
        self.register_prep(accounts)

        # unregister prep
        tx = self.create_unregister_prep_tx(account)
        tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            account.balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # register prep (unregistered account)
        self.distribute_icx(accounts, init_balance)

        tx = self.create_register_prep_tx(account, register_data)
        tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            account.balance -= tx_result['stepUsed'] * tx_result['stepPrice']
            self.assertEqual(tx_result['status'], 0)

        self.refund_icx(accounts)

    def test_2_register_100_preps(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 101) * ICX_FACTOR
        account_count: int = 100
        accounts: List['Account'] = self.create_accounts(account_count)

        main_preps = self.get_main_prep_list()
        if main_preps['preps']:
            return

        # create
        self.distribute_icx(accounts, init_balance)

        # register prep account0
        self.register_prep(accounts[:1])

        # getPRepList
        preps = self.get_prep_list()['preps']
        prep_addresses = list(map(lambda prep_list: prep_list['address'], preps))
        self.assertIn(accounts[0].wallet.address, prep_addresses)

        # getSubPRepList
        sub_preps = self.get_sub_prep_list()['preps']
        self.assertFalse(sub_preps)

        # getMainPRepList
        main_preps = self.get_main_prep_list()['preps']
        self.assertFalse(main_preps)

        # register prep account 1~9
        self.register_prep(accounts[1:10])

        # getPRepList
        preps = self.get_prep_list()['preps']
        prep_addresses = list(map(lambda prep_list: prep_list['address'], preps))
        for account in accounts[:10]:
            self.assertIn(account.wallet.address, prep_addresses)

        # getSubPRepList
        sub_preps = self.get_sub_prep_list()['preps']
        self.assertFalse(sub_preps)

        # getMainPRepList
        main_preps = self.get_main_prep_list()['preps']
        self.assertFalse(main_preps)

        # register prep account 11~99
        self.register_prep(accounts[10:100])

        # getPRepList
        preps = self.get_prep_list()['preps']
        prep_addresses = list(map(lambda prep_list: prep_list['address'], preps))
        for i, account in enumerate(accounts):
            self.assertIn(account.wallet.address, prep_addresses)

        # getSubPRepList
        sub_preps = self.get_sub_prep_list()['preps']
        self.assertFalse(sub_preps)

        # getMainPRepList
        main_preps = self.get_main_prep_list()['preps']
        self.assertFalse(main_preps)

        # stake 100 icx each accounts
        self.set_stake(accounts, 100*ICX_FACTOR)

        # delegate n icx each accounts
        delegate_info: List[Tuple['Account', int]] = \
            [(prep, (i+1) * ICX_FACTOR) for i, prep in enumerate(accounts)]
        tx_list = []
        for i, delegate in enumerate(delegate_info):
            tx = self.create_set_delegation_tx(accounts[i], [delegate])
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # check data sorted properly and totalDelegated
        preps_info = self.get_prep_list(1, 100)
        preps = preps_info['preps']
        prep_addresses = list(map(lambda prep_list: prep_list['address'], preps))
        for i, account in enumerate(reversed(accounts)):
            self.assertEqual(account.wallet.address, prep_addresses[i])

        preps_info = self.get_prep_list(1, 20)
        preps = preps_info['preps']
        prep_addresses = list(map(lambda prep_list: prep_list['address'], preps))
        for i, account in enumerate(reversed(accounts[80:100])):
            self.assertEqual(account.wallet.address, prep_addresses[i])

        # unregister preps
        tx_list = []
        for i, account in enumerate(accounts):
            tx = self.create_unregister_prep_tx(account)
            tx_list.append(tx)

        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']
        self.refund_icx(accounts)

    def test_3_set_prep(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        account_count: int = 1
        accounts: List['Account'] = self.create_accounts(account_count)
        account = accounts[0]

        # create
        self.distribute_icx(accounts, init_balance)

        keys = [ConstantKeys.P2P_ENDPOINT, ConstantKeys.PUBLIC_KEY, ConstantKeys.WEBSITE, ConstantKeys.DETAILS,
                ConstantKeys.EMAIL, ConstantKeys.NAME]
        register_data = self._create_register_prep_params(account)

        # register prep with invalid data
        for key in keys:
            data = copy.deepcopy(register_data)
            data[key] = ''
            tx = self.create_register_prep_tx(account, data)
            tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
            self.process_confirm_block_tx(self.icon_service)
            tx_results = self.get_txresults(self.icon_service, tx_hashes)
            for i, tx_result in enumerate(tx_results):
                self.assertEqual(tx_result['status'], 0)
                account.balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # register prep
        self.register_prep(accounts)

        set_data = copy.deepcopy(register_data)
        endpoint = "127.0.0.1:9000"
        website = "https://website.example.com"
        details = "https://website.example.com/details.json"
        email = "myemail@my.email"
        name = "newname"
        set_data[ConstantKeys.P2P_ENDPOINT] = endpoint
        set_data[ConstantKeys.WEBSITE] = website
        set_data[ConstantKeys.DETAILS] = details
        set_data[ConstantKeys.EMAIL] = email
        set_data[ConstantKeys.NAME] = name
        del set_data[ConstantKeys.PUBLIC_KEY]
        tx = self.create_set_prep_tx(account, set_data=set_data)
        tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            account.balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        prep = self.get_prep(account)
        for key in set_data:
            self.assertEqual(set_data[key], prep[key])

        # set irep on pre-vote
        set_data2 = copy.deepcopy(set_data)
        endpoint = "127.0.0.2:9000"
        website = "https://website.example2.com"
        details = "https://website.example2.com/details.json"
        email = "myemail@my2.email"
        name = "newname2"
        set_data2[ConstantKeys.P2P_ENDPOINT] = endpoint
        set_data2[ConstantKeys.WEBSITE] = website
        set_data2[ConstantKeys.DETAILS] = details
        set_data2[ConstantKeys.EMAIL] = email
        set_data2[ConstantKeys.NAME] = name
        tx = self.create_set_prep_tx(account, irep=45_000*ICX_FACTOR, set_data=set_data2)
        tx_hashes = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 0)
            account.balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        prep = self.get_prep(account)
        for key in set_data:
            self.assertEqual(set_data[key], prep[key])

        tx_list = []
        for i, account in enumerate(accounts):
            tx = self.create_unregister_prep_tx(account)
            tx_list.append(tx)

        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)

        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']
        self.refund_icx(accounts)

    def test_4_register_prep_country(self):
        init_balance: int = (PREP_REGISTER_COST_ICX + 1) * ICX_FACTOR
        account_count: int = 2
        accounts: List['Account'] = self.create_accounts(account_count)

        # create
        self.distribute_icx(accounts, init_balance)

        user0_register_data = self._create_register_prep_params(accounts[0])
        user1_register_data = self._create_register_prep_params(accounts[1])

        # user0 register with invalid country code and user1 register with valid country
        user0_register_data[ConstantKeys.COUNTRY] = "ABC"
        user1_register_data[ConstantKeys.COUNTRY] = "USA"
        user_data = [user0_register_data, user1_register_data]
        tx_list = []
        for i, account in enumerate(accounts):
            tx = self.create_register_prep_tx(account, user_data[i])
            tx_list.append(tx)
        tx_hashes = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(tx_result['status'], 1)
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice'] + PREP_REGISTER_COST_ICX * ICX_FACTOR

        prep0 = self.get_prep(accounts[0])
        prep1 = self.get_prep(accounts[1])

        self.assertEqual("ZZZ", prep0[ConstantKeys.COUNTRY])
        self.assertEqual("USA", prep1[ConstantKeys.COUNTRY])

        self.refund_icx(accounts)
