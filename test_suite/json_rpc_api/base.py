import os
from typing import Dict, Union, List, Tuple, Optional

from iconcommons import IconConfig
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, TransactionBuilder, CallTransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.type_converter_templates import ConstantKeys
from tbears.config.tbears_config import tbears_server_config, ConfigKey
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

DEFAULT_STEP_LIMIT = 1_000_000
DEFAULT_SCORE_CALL_STEP_LIMIT = 10_000_000
DEFAULT_DEPLOY_STEP_LIMIT = 100_000_000_000

DEFAULT_NID = 3
SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"
GOVERNANCE_ADDRESS = "cx0000000000000000000000000000000000000001"
TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

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

        super().setUp(block_confirm_interval=block_confirm_interval,
                      network_only=True,
                      network_delay_ms=self.config[ConfigKey.NETWORK_DELAY_MS])
        self.icon_service = IconService(HTTPProvider(TEST_HTTP_ENDPOINT_URI_V3))
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
            self.process_message_tx_without_txresult(self.icon_service,
                                                     self._test1,
                                                     self._genesis,
                                                     msg="test message")
            self.process_confirm_block_tx(self.icon_service)
            block_height += 1

    def _make_blocks_to_end_calculation(self) -> int:
        iiss_info = self.get_iiss_info()
        next_calculation = int(iiss_info.get('nextCalculation', 0), 16)

        self._make_blocks(to=next_calculation - 1)

        self.assertEqual(self._get_block_height(), next_calculation - 1)
        return next_calculation - 1

    @staticmethod
    def create_deploy_score_tx(score_path: str, from_: 'TestAccount',
                               to: str = SCORE_INSTALL_ADDRESS) -> 'SignedTransaction':
        transaction = DeployTransactionBuilder() \
            .from_(from_.wallet.get_address()) \
            .to(to) \
            .step_limit(DEFAULT_DEPLOY_STEP_LIMIT) \
            .nid(DEFAULT_NID) \
            .nonce(0) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(score_path)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_set_revision_tx(from_: 'TestAccount', revision: int) -> 'SignedTransaction':
        # set revision
        transaction = CallTransactionBuilder() \
            .from_(from_.wallet.get_address()) \
            .to(GOVERNANCE_ADDRESS) \
            .step_limit(DEFAULT_SCORE_CALL_STEP_LIMIT) \
            .nid(3) \
            .nonce(100) \
            .method("setRevision") \
            .params({"code": revision, "name": f"1.4.{revision}"}) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_transfer_icx_tx(from_: 'TestAccount',
                               to_: Union['TestAccount', str],
                               value: int,
                               step_limit: int = DEFAULT_STEP_LIMIT,
                               nid: int = DEFAULT_NID,
                               nonce: int = 0) -> 'SignedTransaction':

        if isinstance(to_, TestAccount):
            to_ = to_.wallet.get_address()

        transaction = TransactionBuilder() \
            .from_(from_.wallet.get_address()) \
            .to(to_) \
            .value(value) \
            .step_limit(step_limit) \
            .nid(nid) \
            .nonce(nonce) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_.wallet)
        return signed_transaction

    @staticmethod
    def create_register_prep_tx(account: 'TestAccount',
                                reg_data: Dict[str, Union[str, bytes]] = None,
                                value: int = 2000 * ICX_FACTOR,
                                step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                nid: int = DEFAULT_NID,
                                nonce: int = 0) -> 'SignedTransaction':
        if not reg_data:
            reg_data = Base._create_register_prep_params(account)

        transaction = CallTransactionBuilder(). \
            from_(account.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("registerPRep"). \
            params(reg_data). \
            build()

        signed_transaction = SignedTransaction(transaction, account.wallet)
        return signed_transaction

    @staticmethod
    def create_unregister_prep_tx(account: 'TestAccount',
                                  value: int = 0,
                                  step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                  nid: int = DEFAULT_NID,
                                  nonce: int = 0) -> 'SignedTransaction':

        transaction = CallTransactionBuilder(). \
            from_(account.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("unregisterPRep"). \
            build()

        signed_transaction = SignedTransaction(transaction, account.wallet)
        return signed_transaction

    @staticmethod
    def create_set_prep_tx(account: 'TestAccount',
                           irep: int = None,
                           set_data: Dict[str, Union[str, bytes]] = None,
                           value: int = 0,
                           step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                           nid: int = DEFAULT_NID,
                           nonce: int = 0) -> 'SignedTransaction':
        if set_data is None:
            set_data = {}
        if irep is not None:
            set_data[ConstantKeys.IREP] = hex(irep)

        transaction = CallTransactionBuilder(). \
            from_(account.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setPRep"). \
            params(set_data). \
            build()

        signed_transaction = SignedTransaction(transaction, account.wallet)
        return signed_transaction

    @staticmethod
    def create_set_stake_tx(account: 'TestAccount',
                            stake: int,
                            value: int = 0,
                            step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                            nid: int = DEFAULT_NID,
                            nonce: int = 0) -> 'SignedTransaction':

        transaction = CallTransactionBuilder(). \
            from_(account.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setStake"). \
            params({"value": hex(stake)}). \
            build()

        signed_transaction = SignedTransaction(transaction, account.wallet)
        return signed_transaction

    @staticmethod
    def create_set_delegation_tx(account: 'TestAccount',
                                 delegations: List[Tuple['TestAccount', int]],
                                 value: int = 0,
                                 step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                                 nid: int = DEFAULT_NID,
                                 nonce: int = 0) -> 'SignedTransaction':
        delegations = Base.create_delegation_params(delegations)

        transaction = CallTransactionBuilder(). \
            from_(account.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setDelegation"). \
            params({"delegations": delegations}). \
            build()

        signed_transaction = SignedTransaction(transaction, account.wallet)
        return signed_transaction

    @staticmethod
    def create_claim_iscore_tx(account: 'TestAccount',
                               value: int = 0,
                               step_limit: int = DEFAULT_SCORE_CALL_STEP_LIMIT,
                               nid: int = DEFAULT_NID,
                               nonce: int = 0) -> 'SignedTransaction':

        transaction = CallTransactionBuilder(). \
            from_(account.wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("claimIScore"). \
            build()

        signed_transaction = SignedTransaction(transaction, account.wallet)
        return signed_transaction

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
            .method("getPRepList") \
            .params(params) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_main_prep_list(self) -> dict:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getMainPRepList") \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_sub_prep_list(self) -> dict:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getSubPRepList") \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_prep(self,
                 prep: Union['TestAccount', str]) -> dict:

        if isinstance(prep, TestAccount):
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
                  address: Union['TestAccount', str]) -> dict:

        if isinstance(address, TestAccount):
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
                       address: Union['TestAccount', str]) -> dict:

        if isinstance(address, TestAccount):
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
                    address: Union['TestAccount', str]) -> int:

        if isinstance(address, TestAccount):
            address = address.wallet.get_address()

        return self.icon_service.get_balance(address)

    def get_step_price(self) -> int:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(GOVERNANCE_ADDRESS) \
            .method("getStepPrice") \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def query_iscore(self,
                     address: Union['TestAccount', str]) -> dict:

        if isinstance(address, TestAccount):
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
    def _create_register_prep_params(account: 'TestAccount') -> Dict[str, Union[str, bytes]]:
        name = f"node{account.wallet.get_address()}"

        return {
            ConstantKeys.NAME: name,
            ConstantKeys.COUNTRY: "ZZZ",
            ConstantKeys.CITY: "Unknown",
            ConstantKeys.EMAIL: f"{name}@example.com",
            ConstantKeys.WEBSITE: f"https://{name}.example.com",
            ConstantKeys.DETAILS: f"https://{name}.example.com/details",
            ConstantKeys.P2P_ENDPOINT: f"{name}.example.com:7100",
            ConstantKeys.PUBLIC_KEY: f"0x{account.wallet.bytes_public_key.hex()}"
        }

    @staticmethod
    def create_delegation_params(params: List[Tuple['TestAccount', int]]) -> List[Dict[str, str]]:
        return [{"address": account.wallet.get_address(), "value": hex(value)}
                for (account, value) in params
                if value > 0]

    def load_admin(self) -> 'TestAccount':
        balance: int = self.get_balance(self._test1.get_address())
        return TestAccount(self._test1, balance)

    def load_test_accounts(self) -> List['TestAccount']:
        accounts: List['TestAccount'] = []
        for wallet in self._wallet_array:
            balance: int = self.get_balance(wallet)
            accounts.append(TestAccount(wallet, balance))
        return accounts

    @staticmethod
    def create_accounts(count: int) -> list:
        accounts: list = []
        wallets: List['KeyWallet'] = [KeyWallet.create() for _ in range(count)]
        for wallet in wallets:
            accounts.append(TestAccount(wallet))
        return accounts

    # ============================================================= #
    def distribute_icx(self, accounts: List['TestAccount'], init_balance: int):
        admin: 'TestAccount' = self.load_admin()
        tx_list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(admin, account, init_balance)
            tx_list.append(tx)

        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(True, tx_result['status'])
            accounts[i].balance += init_balance

    def set_stake(self, accounts: List['TestAccount'], stake_value: int):
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_set_stake_tx(account, stake_value)
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(True, tx_result['status'])
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

    def set_delegation(self, accounts: List['TestAccount'], origin_delegations_list: list):
        tx_list: list = []
        for i, account in enumerate(accounts):
            tx: 'SignedTransaction' = self.create_set_delegation_tx(account, origin_delegations_list[i])
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(True, tx_result['status'])
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']

    def register_prep(self, accounts: List['TestAccount']):
        tx_list: list = []
        for account in accounts:
            tx: 'SignedTransaction' = self.create_register_prep_tx(account)
            tx_list.append(tx)
        tx_hashes: list = self.process_transaction_bulk_without_txresult(tx_list, self.icon_service)
        self.process_confirm_block_tx(self.icon_service)
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for i, tx_result in enumerate(tx_results):
            self.assertEqual(True, tx_result['status'])
            accounts[i].balance -= PREP_REGISTER_COST_ICX * ICX_FACTOR
            accounts[i].balance -= tx_result['stepUsed'] * tx_result['stepPrice']


class TestAccount:
    def __init__(self, wallet: 'KeyWallet' = None, balance: int = 0):
        self.wallet: 'KeyWallet' = wallet
        self.balance: int = balance
