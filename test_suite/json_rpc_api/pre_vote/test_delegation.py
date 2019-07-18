from typing import TYPE_CHECKING, List, Tuple, Dict

from iconservice.icon_constant import ConfigKey, IISS_MAX_DELEGATIONS

from test_suite.json_rpc_api.base import Base, ICX_FACTOR

if TYPE_CHECKING:
    from iconsdk.signed_transaction import SignedTransaction
    from test_suite.json_rpc_api.base import TestAccount
    from iconsdk.builder.transaction_builder import Transaction


class TestDelegation(Base):
    def test_delegate1(self):
        init_balance: int = 1000 * ICX_FACTOR
        account_count: int = 1
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # create
        self.distribute_icx(accounts, init_balance)

        # set stake
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # set delegation
        delegation_value: int = stake_value
        origin_delegations_list: list = [[(accounts[0], delegation_value)]]
        tx: 'Transaction' = self.create_set_delegation_tx_without_sign(accounts[0], origin_delegations_list[0])
        estimate_step: int = self.estimate_step(tx)

    def test_delegate3(self):
        init_balance: int = 3000 * ICX_FACTOR
        account_count: int = 2
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # create user0 ~ 1
        self.distribute_icx(accounts, init_balance)

        # register prep user0
        self.register_prep(accounts[:1])

        # set stake user0 ~ 1 100%
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake user0 ~ 1 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # set delegation user0 to user1 100%
        delegation_value: int = stake_value
        origin_delegations_list: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations_list)

        # get delegation user0 100%
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # set delegation user0 to user 1 50%
        delegation_value: int = stake_value // 2
        origin_delegations_list: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations_list)

        # get delegation user0 50%
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # set delegation user0 to user1 0%
        delegation_value: int = 0
        origin_delegations_list: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations_list)

        # get delegation user0 0%
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # set stake users 0% again
        stake_value: int = 0
        self.set_stake(accounts, stake_value)

        # make blocks
        prev_block: int = self._get_block_height()
        max_expired_block_height: int = self.config[ConfigKey.IISS_META_DATA][ConfigKey.UN_STAKE_LOCK_MAX]
        self._make_blocks(prev_block + max_expired_block_height + 1)

        # get balance
        for account in accounts:
            response: int = self.get_balance(account)
            expected_result: int = account.balance
            self.assertEqual(expected_result, response)

    def test_delegate4(self):
        init_balance: int = 3000 * ICX_FACTOR
        account_count: int = 2
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # create user0 ~ 1
        self.distribute_icx(accounts, init_balance)

        # register prep user0 ~ 1
        self.register_prep(accounts)

        # set stake user0 ~ 1 100%
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake user0 ~ 1 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # set delegation user0 to user1 100%
        delegation_value: int = stake_value
        origin_delegations_list: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations_list)

        # get delegation user0 to user1 100%
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # set delegation user0 to user1 50%
        delegation_value: int = stake_value // 2
        origin_delegations_list: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations_list)

        # get delegation user0 to user1 50%
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # set delegate user1 0%
        delegation_value: int = 0
        origin_delegations_list: list = [[(accounts[1], delegation_value)]]
        self.set_delegation(accounts[:1], origin_delegations_list)

        # get delegate user1 0%
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # set stake users 0% again
        stake_value: int = 0
        self.set_stake(accounts, stake_value)

        # make blocks
        prev_block: int = self._get_block_height()
        max_expired_block_height: int = self.config[ConfigKey.IISS_META_DATA][ConfigKey.UN_STAKE_LOCK_MAX]
        self._make_blocks(prev_block + max_expired_block_height + 1)

        # get balance
        for account in accounts:
            response: int = self.get_balance(account)
            expected_result: int = account.balance
            self.assertEqual(expected_result, response)

    def test_delegate5(self):
        init_balance: int = 3000 * ICX_FACTOR
        account_count: int = 3
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # create user0 ~ 2
        self.distribute_icx(accounts, init_balance)

        # register prep user0 ~ 2
        self.register_prep(accounts)

        # set stake user0 ~ 2 100%
        stake_value: int = 100
        self.set_stake(accounts, stake_value)

        # get stake user0 ~ 1 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # == case 1 == #
        start_index: int = 0
        delegation_cnt: int = 2
        delegation_value: int = stake_value // delegation_cnt

        # set delegation user0 to user0 ~ 1 each 50%
        origin_delegations_list: list = []
        origin_delegations: List[Tuple['TestAccount', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        origin_delegations_list.append(origin_delegations)
        self.set_delegation(accounts[:1], origin_delegations_list)

        # query
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # == case 2 == #
        start_index: int = 1
        delegation_cnt: int = 2
        delegation_value: int = stake_value // delegation_cnt

        # set delegation user0 to user1 ~ 2 each 50%
        origin_delegations_list: list = []
        origin_delegations: List[Tuple['TestAccount', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        origin_delegations_list.append(origin_delegations)
        self.set_delegation(accounts[:1], origin_delegations_list)

        # query
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # set stake users 0% again
        stake_value: int = 0
        self.set_stake(accounts, stake_value)

        # make blocks
        prev_block: int = self._get_block_height()
        max_expired_block_height: int = self.config[ConfigKey.IISS_META_DATA][ConfigKey.UN_STAKE_LOCK_MAX]
        self._make_blocks(prev_block + max_expired_block_height + 1)

        # get balance
        for account in accounts:
            response: int = self.get_balance(account)
            expected_result: int = account.balance
            self.assertEqual(expected_result, response)

    def test_delegate6(self):
        init_balance: int = 3000 * ICX_FACTOR
        account_count: int = 40
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # create user0 ~ 39
        self.distribute_icx(accounts, init_balance)

        # register prep user0 ~ 39
        self.register_prep(accounts)

        # set stake user0 ~ 39 100%
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake user0 ~ 39 100%
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # == case 1 == #
        start_index: int = 0
        delegation_cnt: int = IISS_MAX_DELEGATIONS
        delegation_value: int = stake_value // delegation_cnt

        # set delegation user0 to user0 ~ 9 each 10%
        origin_delegations_list: list = []
        origin_delegations: List[Tuple['TestAccount', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        origin_delegations_list.append(origin_delegations)
        self.set_delegation(accounts[:1], origin_delegations_list)

        # query
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # == case 2 == #
        start_index: int = 10
        delegation_cnt: int = IISS_MAX_DELEGATIONS
        delegation_value: int = stake_value // delegation_cnt

        # set delegation user0 to user10 ~ 19 each 10%
        origin_delegations_list: list = []
        origin_delegations: List[Tuple['TestAccount', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        origin_delegations_list.append(origin_delegations)
        self.set_delegation(accounts[:1], origin_delegations_list)

        # query
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        prev_origin_delegations_list: list = origin_delegations_list

        # == case 3 (Fail) == #
        start_index: int = 20
        delegation_cnt: int = IISS_MAX_DELEGATIONS + 1
        delegation_value: int = stake_value // delegation_cnt

        # set over delegation user0 to user20 ~ 29 + 1
        tx_list: list = []
        origin_delegations_list: list = []
        origin_delegations: List[Tuple['TestAccount', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        origin_delegations_list.append(origin_delegations)
        for i, account in enumerate(accounts[:1]):
            tx: 'SignedTransaction' = self.create_set_delegation_tx(account, origin_delegations_list[i])
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(False, tx_result['status'])
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

        # case 2 result check again
        delegation_cnt: int = IISS_MAX_DELEGATIONS
        delegation_value: int = stake_value // delegation_cnt
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = \
            self.create_delegation_params(prev_origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # == case 4 == #
        start_index: int = 0
        delegation_cnt: int = IISS_MAX_DELEGATIONS
        delegation_value: int = 0

        # set delegate all users 0loop
        origin_delegations_list: list = []
        origin_delegations: List[Tuple['TestAccount', int]] = []
        for i in range(start_index, start_index + delegation_cnt):
            origin_delegations.append((accounts[i], delegation_value))
        origin_delegations_list.append(origin_delegations)
        self.set_delegation(accounts[:1], origin_delegations_list)

        # query
        user_id: int = 0
        expected_delegations: List[Dict[str, str]] = self.create_delegation_params(origin_delegations_list[user_id])
        expected_total_delegation: int = delegation_value * delegation_cnt
        expected_voting_power: int = stake_value - expected_total_delegation
        expected_result: dict = {
            "delegations": expected_delegations,
            "totalDelegated": hex(expected_total_delegation),
            "votingPower": hex(expected_voting_power)
        }
        response: dict = self.get_delegation(accounts[user_id])
        self.assertEqual(expected_result, response)

        # set stake users 0% again
        stake_value: int = 0
        self.set_stake(accounts, stake_value)

        # make blocks
        prev_block: int = self._get_block_height()
        max_expired_block_height: int = self.config[ConfigKey.IISS_META_DATA][ConfigKey.UN_STAKE_LOCK_MAX]
        self._make_blocks(prev_block + max_expired_block_height + 1)

        # get balance
        for account in accounts:
            response: int = self.get_balance(account)
            expected_result: int = account.balance
            self.assertEqual(expected_result, response)

    def test_delegate7(self):
        init_balance: int = 3000 * ICX_FACTOR
        account_count: int = 100
        accounts: List['TestAccount'] = self.create_accounts(account_count)
        init_block_height: int = self._get_block_height()

        # create user0 ~ 99
        self.distribute_icx(accounts, init_balance)

        # register prep0 ~ 99
        self.register_prep(accounts)

        # set stake
        stake_value: int = 100 * ICX_FACTOR
        self.set_stake(accounts, stake_value)

        # get stake
        for account in accounts:
            response: dict = self.get_stake(account)
            expected_result: dict = {
                "stake": hex(stake_value)
            }
            self.assertEqual(expected_result, response)

        # set delegation
        origin_delegations_list: list = []
        expected_delegation_values: dict = {}
        for i, wallet in enumerate(accounts):
            expected_delegation_values[i] = 0
            total_delegation_value: int = (stake_value - i) // 2
            delegation_cnt: int = i % IISS_MAX_DELEGATIONS
            origin_delegations: List[Tuple['TestAccount', int]] = []
            for j in range(delegation_cnt):
                delegation_value: int = total_delegation_value // delegation_cnt
                expected_delegation_values[j] += delegation_value

                origin_delegations.append((accounts[j], delegation_value))
            origin_delegations_list.append(origin_delegations)
        self.set_delegation(accounts, origin_delegations_list)

        # get delegation
        for i in range(account_count):
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
            response: dict = self.get_delegation(accounts[i])
            self.assertEqual(expected_result, response)

        # get prep
        for i, account in enumerate(accounts):
            response: dict = self.get_prep(account)
            self.assertEqual(hex(stake_value), response["stake"])
            self.assertEqual(hex(expected_delegation_values[i]), response["delegated"])

        # set delegation 0
        origin_delegations_list: list = [[]] * account_count
        self.set_delegation(accounts, origin_delegations_list)

        for account in accounts:
            expected_voting_power: int = stake_value
            expected_result: dict = {
                "delegations": [],
                "totalDelegated": hex(0),
                "votingPower": hex(expected_voting_power)
            }
            response: dict = self.get_delegation(account)
            self.assertEqual(expected_result, response)

        # get prep
        for i, wallet in enumerate(accounts):
            response: dict = self.get_prep(wallet)
            self.assertEqual(hex(stake_value), response["stake"])
            self.assertEqual(hex(0), response["delegated"])

        # set stake users 0% again
        stake_value: int = 0
        self.set_stake(accounts, stake_value)

        # make blocks
        prev_block: int = self._get_block_height()
        max_expired_block_height: int = self.config[ConfigKey.IISS_META_DATA][ConfigKey.UN_STAKE_LOCK_MAX]
        self._make_blocks(prev_block + max_expired_block_height + 1)

        # get balance
        for account in accounts:
            response: int = self.get_balance(account)
            expected_result: int = account.balance
            self.assertEqual(expected_result, response)
