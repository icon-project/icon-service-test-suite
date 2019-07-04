from typing import TYPE_CHECKING, List, Tuple, Dict

from iconsdk.wallet.wallet import KeyWallet

from .base import Base, ICX_FACTOR

if TYPE_CHECKING:
    from iconsdk.signed_transaction import SignedTransaction


class TestDelegation(Base):
    def test_delegate3(self):
        init_balance: int = 1000 * ICX_FACTOR
        init_account_count: int = 2
        init_block_height: int = self._get_block_height()

        # create user0 ~ 1
        accounts: List['KeyWallet'] = [KeyWallet.create() for _ in range(init_account_count)]
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, account, init_balance)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # register prep user0
        tx: 'SignedTransaction' = self.create_register_prep_tx(accounts[0])
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # set stake user0 ~ 1 100%
        stake_value: int = 100 * ICX_FACTOR
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # get stake user0 ~ 1 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # set delegate user1 100%
        delegation_value: int = stake_value
        origin_delegations: List[Tuple['KeyWallet', int]] = [(accounts[1], delegation_value)]
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user1 100%
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

        # set delegate user1 50%
        delegation_value: int = stake_value // 2
        origin_delegations: List[Tuple['KeyWallet', int]] = [(accounts[1], delegation_value)]
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user1 50%
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

        # set delegate user1 0%
        delegation_value: int = 0
        origin_delegations: List[Tuple['KeyWallet', int]] = [(accounts[1], delegation_value)]
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user1 0%
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

    def test_delegate4(self):
        init_balance: int = 1000 * ICX_FACTOR
        init_account_count: int = 2
        init_block_height: int = self._get_block_height()

        # create user0 ~ 1
        accounts: List['KeyWallet'] = [KeyWallet.create() for _ in range(init_account_count)]
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, account, init_balance)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # register prep user0 ~ 1
        for account in accounts:
            tx: 'SignedTransaction' = self.create_register_prep_tx(account)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # set stake user0 ~ 1 100%
        stake_value: int = 100 * ICX_FACTOR
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # get stake user0 ~ 1 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # set delegate user1 100%
        delegation_value: int = stake_value
        origin_delegations: List[Tuple['KeyWallet', int]] = [(accounts[1], delegation_value)]
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user1 100%
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

        # set delegate user1 50%
        delegation_value: int = stake_value // 2
        origin_delegations: List[Tuple['KeyWallet', int]] = [(accounts[1], delegation_value)]
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user1 50%
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

        # set delegate user1 0%
        delegation_value: int = 0
        origin_delegations: List[Tuple['KeyWallet', int]] = [(accounts[1], delegation_value)]
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user1 0%
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

    def test_delegate5(self):
        init_balance: int = 1000
        init_account_count: int = 3
        init_block_height: int = self._get_block_height()

        # create user0 ~ 2
        accounts: List['KeyWallet'] = [KeyWallet.create() for _ in range(init_account_count)]
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, account, init_balance)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # register prep user0 ~ 2
        for account in accounts:
            tx: 'SignedTransaction' = self.create_register_prep_tx(account)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # set stake user0 ~ 2 100%
        stake_value: int = 100
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # get stake user0 ~ 1 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        start_index: int = 0
        delegation_cnt: int = 2
        # set delegate user0 to user0 ~ 1 each 50%
        delegation_value: int = stake_value // delegation_cnt
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user0 to user0 ~ 1 each 50%
        delegation_value: int = stake_value // delegation_cnt
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

        start_index: int = 1
        delegation_cnt: int = 2
        # set delegate user0 to user1 ~ 2 each 50%
        delegation_value: int = stake_value // delegation_cnt
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user0 to user0 ~ 1 each 50%
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

    def test_delegate6(self):
        init_balance: int = 1000 * ICX_FACTOR
        init_account_count: int = 40
        init_block_height: int = self._get_block_height()

        # create user0 ~ 39
        accounts: List['KeyWallet'] = [KeyWallet.create() for _ in range(init_account_count)]
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, account, init_balance)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # register prep user0 ~ 39
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_register_prep_tx(account)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # set stake user0 ~ 39 100%
        stake_value: int = 100 * ICX_FACTOR
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # get stake user0 ~ 39 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        max_delegates: int = 10

        start_index: int = 0
        delegation_cnt: int = max_delegates
        # set delegate user0 to user0 ~ 9 each 10%
        delegation_value: int = stake_value // delegation_cnt
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user0 to user0 ~ 9 each 10%
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

        start_index: int = 10
        delegation_cnt: int = max_delegates
        # set delegate user0 to user10 ~ 19 each 10%
        delegation_value: int = stake_value // delegation_cnt
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate user0 to user10 ~ 19 each 10%
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

        start_index: int = 20
        delegation_cnt: int = max_delegates + 1
        # set over delegate user20 ~ 29 + 1 (Fail)
        delegation_value: int = stake_value // delegation_cnt
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt + 1):
            origin_delegations.append((accounts[i], delegation_value))
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(False, tx_result['status'])

        start_index: int = 10
        delegation_cnt: int = max_delegates
        delegation_value: int = stake_value // delegation_cnt
        # get delegate rollback [user10 ~ 19]
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

        start_index: int = 0
        delegation_cnt: int = max_delegates
        # set delegate all users 0loop
        delegation_value: int = 0
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[0], origin_delegations)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])

        # get delegate all users 0loop
        origin_delegations: List[Tuple['KeyWallet', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[0])
        self.assertEqual(expected_result, response)

    def test_delegate7(self):
        init_balance: int = 1000 * ICX_FACTOR
        init_account_count: int = 100
        init_block_height: int = self._get_block_height()

        accounts: List['KeyWallet'] = [KeyWallet.create() for _ in range(init_account_count)]
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, account, init_balance)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # register prep
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_register_prep_tx(account)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # set stake
        stake_value: int = 100 * ICX_FACTOR
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(True, tx_result['status'])

        # get stake
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        max_delegates: int = 10

        # set delegate
        expected_delegation_values: dict = {}
        tx_list: list = []
        for i, account in enumerate(accounts):
            expected_delegation_values[i] = 0
            total_delegation_value: int = (stake_value - i) // 2
            delegation_cnt: int = i % max_delegates
            origin_delegations: List[Tuple['KeyWallet', int]] = []
            for j in range(delegation_cnt):
                delegation_value: int = total_delegation_value // delegation_cnt
                expected_delegation_values[j] += delegation_value
                origin_delegations.append((accounts[j], delegation_value))
            tx: 'SignedTransaction' = self.create_set_delegation_tx(accounts[i], origin_delegations)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

        # get delegate
        for i in range(init_account_count):
            total_delegation_value: int = (stake_value - i) // 2
            delegation_cnt: int = i % max_delegates
            expected_total_delegation_value: int = 0

            origin_delegations: List[Tuple['KeyWallet', int]] = []
            for j in range(delegation_cnt):
                delegation_value: int = total_delegation_value // delegation_cnt
                expected_total_delegation_value += delegation_value
                origin_delegations.append((accounts[j], delegation_value))
            expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations)
            expected_voting_power: int = stake_value - expected_total_delegation_value
            response: dict = self.get_delegation(accounts[i])
            expected_result: dict = {
                "delegations": expected_delegations,
                "totalDelegated": hex(expected_total_delegation_value),
                "votingPower": hex(expected_voting_power)
            }
            self.assertEqual(expected_result, response)

        # get prep
        for i, account in enumerate(accounts):
            response: dict = self.get_prep(account)
            delegation: dict = response["delegation"]
            expected_result: dict = {
                "stake": hex(stake_value),
                "delegated": hex(expected_delegation_values[i])
            }
            self.assertEqual(expected_result, delegation)

        # set delegate 0
        tx_list: list = []
        for i, account in enumerate(accounts):
            origin_delegations: List[Tuple['KeyWallet', int]] = []
            tx: 'SignedTransaction' = self.create_set_delegation_tx(account, origin_delegations)
            tx_list.append(tx)
        tx_results: list = self.process_transaction_bulk(tx_list, self.icon_service)
        for tx_result in tx_results:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

        # get delegate
        for i, account in enumerate(accounts):
            response: dict = self.get_delegation(account)
            expected_result: dict = {
                "delegations": [],
                "totalDelegated": hex(0),
                "votingPower": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # get prep
        for i, account in enumerate(accounts):
            response: dict = self.get_prep(account)
            delegation: dict = response["delegation"]
            expected_result = {
                "stake": hex(stake_value),
                "delegated": hex(0)
            }
            self.assertEqual(expected_result, delegation)
