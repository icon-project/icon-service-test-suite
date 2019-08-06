import os
from time import sleep
from typing import Dict, Union, List, Tuple, Optional

from iconcommons import IconConfig
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, TransactionBuilder, CallTransactionBuilder, \
    Transaction
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.type_converter_templates import ConstantKeys
from tbears.config.tbears_config import tbears_server_config, ConfigKey
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS
from iconservice.icon_constant import ConfigKey as ISConfigKey

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

DEFAULT_STEP_LIMIT = 1_000_000
DEFAULT_SCORE_CALL_STEP_LIMIT = 10_000_000
DEFAULT_DEPLOY_STEP_LIMIT = 100_000_000_000

DEFAULT_NID = 3
SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"
GOVERNANCE_ADDRESS = "cx0000000000000000000000000000000000000001"
API_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
DEBUG_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/debug/v3"

PREP_REGISTER_COST_ICX = 2000
ICX_FACTOR = 10 ** 18

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
default_config_path = os.path.join(ROOT_PATH, "tbears_server_config.json")


class Base(IconIntegrateTestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config: 'IconConfig' = IconConfig(default_config_path, tbears_server_config)
        cls.config.load()

    def setUp(self):
        if self.config[ConfigKey.BLOCK_MANUAL_CONFIRM]:
            block_confirm_interval: int = 0
        else:
            block_confirm_interval: int = self.config[ConfigKey.BLOCK_CONFIRM_INTERVAL]

        self._block_confirm_empty: bool = self.config[ConfigKey.BLOCK_CONFIRM_EMPTY]

        super().setUp(block_confirm_interval=block_confirm_interval,
                      network_only=True,
                      network_delay_ms=self.config[ConfigKey.NETWORK_DELAY_MS])
        self.icon_service = IconService(HTTPProvider(API_HTTP_ENDPOINT_URI_V3))
        self.icon_service_for_debug = IconService(HTTPProvider(DEBUG_HTTP_ENDPOINT_URI_V3))
        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3

    # ================= Tool =================
    def _get_block_height(self) -> int:
        block_height: int = 0
        if self.icon_service:
            block = self.icon_service.get_block("latest")
            block_height = block['height']
        return block_height

    def _make_blocks(self, to: int):
        block_height = self._get_block_height()

        while to > block_height:
            if self._block_confirm_empty:
                sleep(self._block_confirm_interval / 2)
                block_height: int = self._get_block_height()
            else:
                self.process_message_tx_without_txresult(self.icon_service,
                                                         self._test1,
                                                         self._genesis,
                                                         msg="test message")
                self.process_confirm_block_tx(self.icon_service, 10.0)
                block_height += 1
        self.process_confirm_block_tx(self.icon_service, 50.0)

    def _make_blocks_to_end_calculation(self) -> int:
        iiss_info: dict = self.get_iiss_info()
        next_calculation: int = int(iiss_info.get('nextCalculation', 0), 16)
        cur_block_height: int = self._get_block_height()
        if cur_block_height == next_calculation - 1:
            # last calculate block
            self._make_blocks(to=next_calculation)
            iiss_info: dict = self.get_iiss_info()
            next_calculation: int = int(iiss_info.get('nextCalculation', 0), 16)
        self._make_blocks(to=next_calculation - 1)

        self.assertEqual(self._get_block_height(), next_calculation - 1)
        return next_calculation - 1

    def get_issue_info_after_decentralized(self, start_calc_block, end_calc_block):
        if self.icon_service.get_block(start_calc_block)['confirmed_transaction_list'][0]['dataType'] != 'base':
            return [], 0, 0
        issue_data_of_term = []
        calulated_issue_amount = 0
        actual_issue_amount = 0
        for height in range(start_calc_block, end_calc_block + 1):
            issue_data_per_block = [height]
            calculated_issue_in_block = int(self.icon_service.get_block(height)['confirmed_transaction_list'][0]['data']['prep']['value'], 16)
            calulated_issue_amount += calculated_issue_in_block
            issue_data_per_block.append(calculated_issue_in_block)
            result = self.icon_service.get_block(height)['confirmed_transaction_list'][0]['data']['result']
            issue_data_per_block.append(int(result['coveredByFee'], 16))
            issue_data_per_block.append(int(result['coveredByOverIssuedICX'], 16))
            actual_issue_in_block = int(result['issue'], 16)
            actual_issue_amount += actual_issue_in_block
            issue_data_per_block.append(int(result['issue'], 16))
            issue_data_of_term.append(issue_data_per_block)

        return issue_data_of_term, calulated_issue_amount, actual_issue_amount


    @staticmethod
    def create_deploy_score_tx(score_path: str,
                               from_: 'Account',
                               to_: str = SCORE_INSTALL_ADDRESS) -> 'SignedTransaction':
        transaction: 'Transaction' = Base.create_deploy_score_tx_without_sign(score_path,
                                                                              from_,
                                                                              to_)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_deploy_score_tx_without_sign(score_path: str,
                                            from_: 'Account',
                                            to: str = SCORE_INSTALL_ADDRESS) -> 'Transaction':
        return DeployTransactionBuilder() \
            .from_(from_.wallet.get_address()) \
            .to(to) \
            .step_limit(DEFAULT_DEPLOY_STEP_LIMIT) \
            .nid(DEFAULT_NID) \
            .nonce(0) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(score_path)) \
            .build()

    @staticmethod
    def create_set_revision_tx(from_: 'Account',
                               revision: int) -> 'SignedTransaction':
        transaction: 'Transaction' = Base.create_set_revision_tx_without_sign(from_,
                                                                              revision)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_set_revision_tx_without_sign(from_: 'Account',
                                            revision: int) -> 'Transaction':
        return CallTransactionBuilder() \
            .from_(from_.wallet.get_address()) \
            .to(GOVERNANCE_ADDRESS) \
            .step_limit(DEFAULT_SCORE_CALL_STEP_LIMIT) \
            .nid(3) \
            .nonce(100) \
            .method("setRevision") \
            .params({"code": revision, "name": f"1.4.{revision}"}) \
            .build()

    @staticmethod
    def create_transfer_icx_tx(from_: 'Account',
                               to_: Union['Account', str],
                               value: int,
                               step_limit: int = DEFAULT_STEP_LIMIT,
                               nid: int = DEFAULT_NID,
                               nonce: int = 0) -> 'SignedTransaction':

        transaction: 'Transaction' = Base.create_transfer_icx_tx_without_sign(from_,
                                                                              to_,
                                                                              value,
                                                                              step_limit,
                                                                              nid,
                                                                              nonce)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_transfer_icx_tx_without_sign(from_: 'Account',
                                            to_: Union['Account', str],
                                            value: int,
                                            step_limit: int = DEFAULT_STEP_LIMIT,
                                            nid: int = DEFAULT_NID,
                                            nonce: int = 0) -> 'Transaction':

        if isinstance(to_, Account):
            to_ = to_.wallet.get_address()

        return TransactionBuilder() \
            .from_(from_.wallet.get_address()) \
            .to(to_) \
            .value(value) \
            .step_limit(step_limit) \
            .nid(nid) \
            .nonce(nonce) \
            .build()

    @staticmethod
    def create_register_prep_tx(from_: 'Account',
                                reg_data: Dict[str, Union[str, bytes]] = None,
                                value: int = 2000 * ICX_FACTOR,
                                step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                nid: int = DEFAULT_NID,
                                nonce: int = 0) -> 'SignedTransaction':
        transaction: 'Transaction' = Base.create_register_prep_tx_without_sign(from_,
                                                                               reg_data,
                                                                               value,
                                                                               step_limit,
                                                                               nid,
                                                                               nonce)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_register_prep_tx_without_sign(account: 'Account',
                                             reg_data: Dict[str, Union[str, bytes]] = None,
                                             value: int = 2000 * ICX_FACTOR,
                                             step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                             nid: int = DEFAULT_NID,
                                             nonce: int = 0) -> 'Transaction':
        if not reg_data:
            reg_data = Base._create_register_prep_params(account)

        return CallTransactionBuilder(). \
            from_(account.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("registerPRep"). \
            params(reg_data). \
            build()

    @staticmethod
    def create_unregister_prep_tx(from_: 'Account',
                                  value: int = 0,
                                  step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                  nid: int = DEFAULT_NID,
                                  nonce: int = 0) -> 'SignedTransaction':

        transaction: 'Transaction' = Base.create_unregister_prep_tx_without_sign(from_,
                                                                                 value,
                                                                                 step_limit,
                                                                                 nid,
                                                                                 nonce)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_unregister_prep_tx_without_sign(from_: 'Account',
                                               value: int = 0,
                                               step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                               nid: int = DEFAULT_NID,
                                               nonce: int = 0) -> 'Transaction':

        return CallTransactionBuilder(). \
            from_(from_.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("unregisterPRep"). \
            build()

    @staticmethod
    def create_set_prep_tx(from_: 'Account',
                           irep: int = None,
                           set_data: Dict[str, Union[str, bytes]] = None,
                           value: int = 0,
                           step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                           nid: int = DEFAULT_NID,
                           nonce: int = 0) -> 'SignedTransaction':
        transaction: 'Transaction' = Base.create_set_prep_tx_without_sign(from_,
                                                                          irep,
                                                                          set_data,
                                                                          value,
                                                                          step_limit,
                                                                          nid,
                                                                          nonce)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_set_prep_tx_without_sign(from_: 'Account',
                                        irep: int = None,
                                        set_data: Dict[str, Union[str, bytes]] = None,
                                        value: int = 0,
                                        step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                        nid: int = DEFAULT_NID,
                                        nonce: int = 0) -> 'Transaction':
        if set_data is None:
            set_data = {}
        if irep is not None:
            set_data[ConstantKeys.IREP] = hex(irep)

        return CallTransactionBuilder(). \
            from_(from_.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setPRep"). \
            params(set_data). \
            build()

    @staticmethod
    def create_set_governance_variables_tx(from_: 'Account',
                                           irep: int = 0,
                                           step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                           nid: int = DEFAULT_NID,
                                           nonce: int = 0) -> 'SignedTransaction':
        transaction: 'Transaction' = Base.create_set_governance_variables_tx_without_sign(
            from_,
            irep,
            step_limit,
            0,
            nid,
            nonce)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_set_governance_variables_tx_without_sign(from_: 'Account',
                                                        irep: int = 0,
                                                        step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                                        value: int = 0,
                                                        nid: int = DEFAULT_NID,
                                                        nonce: int = 0) -> 'SignedTransaction':
        return CallTransactionBuilder().\
            from_(from_.wallet.get_address()).\
            to(SYSTEM_ADDRESS).\
            value(value).\
            step_limit(step_limit).\
            nid(nid).\
            nonce(nonce).\
            method("setGovernanceVariables").\
            params({"irep": hex(irep)}).\
            build()

    @staticmethod
    def create_set_stake_tx(from_: 'Account',
                            stake: int,
                            value: int = 0,
                            step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                            nid: int = DEFAULT_NID,
                            nonce: int = 0) -> 'SignedTransaction':

        transaction: 'Transaction' = Base.create_set_stake_tx_without_sign(from_,
                                                                           stake,
                                                                           value,
                                                                           step_limit,
                                                                           nid,
                                                                           nonce)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_set_stake_tx_without_sign(from_: 'Account',
                                         stake: int,
                                         value: int = 0,
                                         step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                         nid: int = DEFAULT_NID,
                                         nonce: int = 0) -> 'Transaction':

        return CallTransactionBuilder(). \
            from_(from_.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setStake"). \
            params({"value": hex(stake)}). \
            build()

    @staticmethod
    def create_set_delegation_tx(from_: 'Account',
                                 delegations: List[Tuple['Account', int]],
                                 value: int = 0,
                                 step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                 nid: int = DEFAULT_NID,
                                 nonce: int = 0) -> 'SignedTransaction':
        transaction: 'Transaction' = Base.create_set_delegation_tx_without_sign(from_,
                                                                                delegations,
                                                                                value,
                                                                                step_limit,
                                                                                nid,
                                                                                nonce)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_set_delegation_tx_without_sign(from_: 'Account',
                                              delegations: List[Tuple['Account', int]],
                                              value: int = 0,
                                              step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                              nid: int = DEFAULT_NID,
                                              nonce: int = 0) -> 'Transaction':
        delegations = Base.create_delegation_params(delegations)

        return CallTransactionBuilder(). \
            from_(from_.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setDelegation"). \
            params({"delegations": delegations}). \
            build()

    @staticmethod
    def create_claim_iscore_tx(from_: 'Account',
                               value: int = 0,
                               step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                               nid: int = DEFAULT_NID,
                               nonce: int = 0) -> 'SignedTransaction':

        transaction: 'Transaction' = Base.create_claim_iscore_tx_without_sign(from_,
                                                                              value,
                                                                              step_limit,
                                                                              nid,
                                                                              nonce)
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_claim_iscore_tx_without_sign(from_: 'Account',
                                            value: int = 0,
                                            step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                            nid: int = DEFAULT_NID,
                                            nonce: int = 0) -> 'Transaction':

        return CallTransactionBuilder(). \
            from_(from_.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("claimIScore"). \
            build()

    def get_prep_list(self,
                      start_index: Optional[int] = None,
                      end_index: Optional[int] = None) -> dict:
        params = {}
        if start_index is not None:
            params['startRanking'] = hex(start_index)
        if end_index is not None:
            params['endRanking'] = hex(end_index)
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getPReps") \
            .params(params) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_main_prep_list(self) -> dict:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getMainPReps") \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_sub_prep_list(self) -> dict:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getSubPReps") \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_prep(self,
                 prep: Union['Account', str]) -> dict:

        if isinstance(prep, Account):
            prep = prep.wallet.get_address()

        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getPRep") \
            .params({"address": prep}) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_stake(self,
                  address: Union['Account', str]) -> dict:

        if isinstance(address, Account):
            address = address.wallet.get_address()

        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getStake") \
            .params({"address": address}) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_delegation(self,
                       address: Union['Account', str]) -> dict:

        if isinstance(address, Account):
            address = address.wallet.get_address()

        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getDelegation") \
            .params({"address": address}) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_balance(self,
                    address: Union['Account', str]) -> int:

        if isinstance(address, Account):
            address = address.wallet.get_address()

        return self.icon_service.get_balance(address)

    def get_step_price(self) -> int:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(GOVERNANCE_ADDRESS) \
            .method("getStepPrice") \
            .build()
        response = self.process_call(call, self.icon_service)
        return int(response, 16)

    def query_iscore(self,
                     address: Union['Account', str]) -> dict:

        if isinstance(address, Account):
            address = address.wallet.get_address()

        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("queryIScore") \
            .params({"address": address}) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_iiss_info(self) -> dict:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getIISSInfo") \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    @staticmethod
    def _create_register_prep_params(account: 'Account') -> Dict[str, Union[str, bytes]]:
        name = f"node{account.wallet.get_address()}"

        return {
            ConstantKeys.NAME: name,
            ConstantKeys.COUNTRY: "KOR",
            ConstantKeys.CITY: "Unknown",
            ConstantKeys.EMAIL: f"{name}@example.com",
            ConstantKeys.WEBSITE: f"https://{name}.example.com",
            ConstantKeys.DETAILS: f"https://{name}.example.com/details",
            ConstantKeys.P2P_ENDPOINT: f"{name}.example.com:7100",
        }

    @staticmethod
    def create_delegation_params(params: List[Tuple['Account', int]]) -> List[Dict[str, str]]:
        return [{"address": account.wallet.get_address(), "value": hex(value)}
                for (account, value) in params
                if value > 0]

    def load_admin(self) -> 'Account':
        balance: int = self.get_balance(self._test1.get_address())
        return Account(self._test1, balance)

    def load_test_accounts(self) -> List['Account']:
        accounts: List['Account'] = []
        for wallet in self._wallet_array:
            balance: int = self.get_balance(wallet.get_address())
            accounts.append(Account(wallet, balance))
        return accounts

    @staticmethod
    def create_accounts(count: int) -> list:
        accounts: list = []
        wallets: List['KeyWallet'] = [KeyWallet.create() for _ in range(count)]
        for wallet in wallets:
            accounts.append(Account(wallet))
        return accounts

    def estimate_step(self, tx: 'Transaction') -> int:
        return self.icon_service_for_debug.estimate_step(tx)

    # ============================================================= #
    def claim_iscore(self, accounts: List["Account"], expected_result: bool = True):
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_claim_iscore_tx(account)
            tx_list.append(tx)

        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, account in enumerate(accounts):
            self.assertEqual(expected_result, tx_results[i]['status'])
            account.balance -= tx_results[i]['stepUsed'] * tx_results[i]['stepPrice']
            if expected_result:
                claimed_icx: str = tx_results[i]['eventLogs'][0]["data"][1]
                account.balance += int(claimed_icx, 16)

    def distribute_icx(self, accounts: List['Account'], init_balance: int, expected_result: bool = True):
        admin: 'Account' = self.load_admin()
        tx_list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(admin, account, init_balance)
            tx_list.append(tx)

        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, account in enumerate(accounts):
            self.assertEqual(expected_result, tx_results[i]['status'])
            account.balance += init_balance

    def set_stake(self, accounts: List['Account'], stake_value: int, expected_result: bool = True):
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, account in enumerate(accounts):
            self.assertEqual(expected_result, tx_results[i]['status'])
            account.balance -= tx_results[i]['stepUsed'] * tx_results[i]['stepPrice']

    def set_delegation(self, accounts: List['Account'], origin_delegations_list: list, expected_result: bool = True):
        tx_list: list = []
        for i, account in enumerate(accounts):
            tx: 'SignedTransaction' = self.create_set_delegation_tx(account, origin_delegations_list[i])
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, account in enumerate(accounts):
            self.assertEqual(expected_result, tx_results[i]['status'])
            account.balance -= tx_results[i]['stepUsed'] * tx_results[i]['stepPrice']

    def register_prep(self, accounts: List['Account'], expected_result: bool = True):
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_register_prep_tx(account)
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, account in enumerate(accounts):
            self.assertEqual(expected_result, tx_results[i]['status'])
            if expected_result:
                account.balance -= PREP_REGISTER_COST_ICX * ICX_FACTOR
                account.balance -= tx_results[i]['stepUsed'] * tx_results[i]['stepPrice']

    def refund_icx(self, accounts: List['Account']):
        new_accounts: List['Account'] = []
        for account in accounts:
            if self.get_balance(account) > 0:
                new_accounts.append(account)

        origin_delegations_list: list = [[]] * len(new_accounts)
        self.set_delegation(new_accounts, origin_delegations_list)

        # set stake users 0% again
        stake_value: int = 0
        self.set_stake(new_accounts, stake_value)

        # make blocks
        prev_block: int = self._get_block_height()
        max_expired_block_height: int = self.config[ISConfigKey.IISS_META_DATA][ISConfigKey.UN_STAKE_LOCK_MAX]
        self._make_blocks(prev_block + max_expired_block_height + 1)

        # get balance
        for account in new_accounts:
            response: int = self.get_balance(account)
            expected_result: int = account.balance
            self.assertEqual(expected_result, response)

        # refund icx
        self._refund_icx(new_accounts)

        # get balance
        for account in new_accounts:
            response: int = self.get_balance(account)
            expected_result: int = 0
            self.assertEqual(expected_result, response)

    def _refund_icx(self, accounts: List['Account']):
        if len(accounts) == 0:
            return

        tx: 'Transaction' = self.create_transfer_icx_tx_without_sign(accounts[0], accounts[0], 0)
        estimate_step: int = self.estimate_step(tx)
        step_price: int = self.get_step_price()
        estimate_fee: int = step_price * estimate_step

        admin: 'Account' = self.load_admin()
        tx_list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(account,
                                                                  admin,
                                                                  account.balance - estimate_fee,
                                                                  step_limit=100_000)
            tx_list.append(tx)

        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account(accounts))
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(True, tx_result['status'])

    def process_confirm_block_tx(self, network: IconService, sleep_ratio: float = 1.0):
        if not self._block_confirm_empty:
            # build message tx
            transaction = TransactionBuilder() \
                .from_(self._test1.get_address()) \
                .to("hx0000000000000000000000000000000000000000") \
                .value(0) \
                .step_limit(10_000_000_000) \
                .nonce(0) \
                .build()

            # signing message tx
            request = SignedTransaction(transaction, self._test1)
            network.send_transaction(request)

        if self._block_confirm_interval > 0:
            sleep(self._block_confirm_interval)
        else:
            sleep_time: float = self._network_delay * sleep_ratio
            if sleep_time > 2.0:
                sleep_time: float = 2.0
            sleep(sleep_time)

    @staticmethod
    def sleep_ratio_from_account(accounts: List["Account"]):
        return min(max(1.0, len(accounts)), 50.0)


class Account:
    def __init__(self, wallet: 'KeyWallet' = None, balance: int = 0):
        self.wallet: 'KeyWallet' = wallet
        self.balance: int = balance
