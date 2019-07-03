import os
from typing import Dict, Union, List, Tuple, Optional

from iconsdk.builder.transaction_builder import DeployTransactionBuilder, TransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

DEFAULT_STEP_LIMIT = 1_000_000
DEFAULT_NID = 3
SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"
GOVERNANCE_ADDRESS = "cx0000000000000000000000000000000000000001"
TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '../'))


class Base(IconIntegrateTestBase):

    def setUp(self):
        super().setUp(block_confirm_interval=1, network_only=True)

        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        self.icon_service = IconService(HTTPProvider(TEST_HTTP_ENDPOINT_URI_V3))

    # ================= Tool =================
    def create_deploy_score_tx(self,
                               score_path: str,
                               from_: 'KeyWallet',
                               to: str = SCORE_INSTALL_ADDRESS) -> 'SignedTransaction':
        # transaction = DeployTransactionBuilder() \
        #     .from_(from_.get_address()) \
        #     .to(to) \
        #     .step_limit(100_000_000_000) \
        #     .nid(DEFAULT_NID) \
        #     .nonce(0) \
        #     .content_type("application/zip") \
        #     .content(gen_deploy_data_content(score_path)) \
        #     .build()
        #
        # # Returns the signed transaction object having a signature
        # signed_transaction = SignedTransaction(transaction, from_)
        # return signed_transaction

    def create_set_revision_tx(self,
                               from_: 'KeyWallet',
                               revision: int) -> 'SignedTransaction':
        # # set revision
        # # Generates a 'setStake' instance of transaction for calling method in SCORE.
        # transaction = TransactionBuilder() \
        #     .from_(from_.get_address()) \
        #     .to(GOVERNANCE_ADDRESS) \
        #     .step_limit(10_000_000) \
        #     .nid(3) \
        #     .nonce(100) \
        #     .method("setRevision") \
        #     .params({"code": 6, "name": "1.4.0"}) \
        #     .build()
        #
        # # Returns the signed transaction object having a signature
        # signed_transaction = SignedTransaction(transaction, from_)
        # return signed_transaction
        pass

    def create_transfer_icx_tx(self,
                               from_: 'KeyWallet',
                               to_: 'KeyWallet',
                               value: int,
                               step_limit: int = DEFAULT_STEP_LIMIT,
                               nid: int = DEFAULT_NID,
                               nonce: int = 0) -> 'SignedTransaction':
        # transaction = TransactionBuilder() \
        #     .from_(from_) \
        #     .to(to_) \
        #     .value(value) \
        #     .step_limit(step_limit) \
        #     .nid(nid) \
        #     .nonce(nonce) \
        #     .build()
        #
        # # Returns the signed transaction object having a signature
        # signed_transaction = SignedTransaction(transaction, self._test1)
        # return signed_transaction
        pass

    def create_register_prep_tx(self,
                                key_wallet: 'KeyWallet',
                                reg_data: Dict[str, Union[str, bytes]] = None,
                                value: int = 0,
                                step_limit: int = DEFAULT_STEP_LIMIT,
                                nid: int = DEFAULT_NID,
                                nonce: int = 0) -> 'SignedTransaction':
        # if not reg_data:
        #     reg_data = self._create_register_prep_params(key_wallet)
        #
        # transaction = CallTransactionBuilder(). \
        #     from_(key_wallet.get_address()). \
        #     to(self.SYSTEM_ADDRESS). \
        #     value(value). \
        #     step_limit(step_limit). \
        #     nid(nid). \
        #     nonce(nonce). \
        #     method("registerPRep"). \
        #     params(reg_data). \
        #     build()
        #
        # signed_transaction = SignedTransaction(transaction, key_wallet)
        #
        # return signed_transaction
        pass

    def create_unregister_prep_tx(self,
                                  key_wallet: 'KeyWallet',
                                  value: int = 0,
                                  step_limit: int = DEFAULT_STEP_LIMIT,
                                  nid: int = DEFAULT_NID,
                                  nonce: int = 0) -> 'SignedTransaction':
        pass

    def create_set_prep_tx(self,
                           key_wallet: 'KeyWallet',
                           irep: int,
                           set_data: Dict[str, Union[str, bytes]] = None,
                           value: int = 0,
                           step_limit: int = DEFAULT_STEP_LIMIT,
                           nid: int = DEFAULT_NID,
                           nonce: int = 0) -> 'SignedTransaction':
        # if not reg_data:
        #     reg_data = self._set_prep_params(key_wallet, irep)
        pass

    def create_set_stake_tx(self,
                            key_wallet: KeyWallet,
                            stake: int,
                            value: int = 0,
                            step_limit: int = DEFAULT_STEP_LIMIT,
                            nid: int = DEFAULT_NID,
                            nonce: int = 0) -> 'SignedTransaction':
        pass

    def create_set_delegation_tx(self,
                                 key_wallet: KeyWallet,
                                 delegations: List[Tuple['KeyWallet', int]],
                                 value: int = 0,
                                 step_limit: int = DEFAULT_STEP_LIMIT,
                                 nid: int = DEFAULT_NID,
                                 nonce: int = 0) -> 'SignedTransaction':
        pass

    def create_claim_iscore_tx(self,
                               key_wallet: 'KeyWallet',
                               value: int = 0,
                               step_limit: int = DEFAULT_STEP_LIMIT,
                               nid: int = DEFAULT_NID,
                               nonce: int = 0) -> 'SignedTransaction':
        pass

    def get_prep_list(self,
                      start_index: Optional[int] = None,
                      end_index: Optional[int] = None) -> dict:
        # params = {}
        # if start_index is not None:
        #     params['startRanking'] = hex(start_index)
        # if end_index is not None:
        #     params['endRanking'] = hex(end_index)
        # call = CallBuilder().from_(self._test1.get_address()) \
        #     .to(self.SYSTEM_ADDRESS) \
        #     .method("getPRepList") \
        #     .params(params) \
        #     .build()
        # response = self.process_call(call, self.icon_service)
        # return response
        pass

    def get_main_prep_list(self) -> dict:
        pass

    def get_sub_prep_list(self) -> dict:
        pass

    def get_prep(self,
                 key_wallet: 'KeyWallet') -> dict:
        pass

    def get_stake(self,
                  key_wallet: 'KeyWallet') -> dict:
        pass

    def get_delegation(self,
                       key_wallet: 'KeyWallet') -> dict:
        pass

    def get_balance(self,
                    key_wallet: 'KeyWallet') -> dict:
        pass

    def query_iscore(self,
                     key_wallet: 'KeyWallet') -> dict:
        pass

    def get_iiss_info(self) -> dict:
        pass

    @staticmethod
    def _create_register_prep_params(key_wallet: 'KeyWallet') -> Dict[str, Union[str, bytes]]:
        # name = f"node{index}"
        #
        # return {
        #     ConstantKeys.NAME: name,
        #     ConstantKeys.EMAIL: f"node{index}@example.com",
        #     ConstantKeys.WEBSITE: f"https://node{index}.example.com",
        #     ConstantKeys.DETAILS: f"https://node{index}.example.com/details",
        #     ConstantKeys.P2P_END_POINT: f"https://node{index}.example.com:7100",
        #     ConstantKeys.PUBLIC_KEY: create_dummy_public_key(name.encode())
        # }
        pass

    @staticmethod
    def _set_prep_params(key_wallet: 'KeyWallet', irep: int) -> Dict[str, Union[str, bytes]]:
        pass

    @staticmethod
    def create_delegation_params(params: List[Tuple['KeyWallet', int]]) -> Dict[str, str]:
        pass