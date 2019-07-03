import os
from typing import Dict, Union, List, Tuple, Optional

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, TransactionBuilder, CallTransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.type_converter_templates import ConstantKeys
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

DEFAULT_STEP_LIMIT = 1_000_000
DEFAULT_NID = 3
SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"
GOVERNANCE_ADDRESS = "cx0000000000000000000000000000000000000001"
TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"


class Base(IconIntegrateTestBase):

    def setUp(self):
        super().setUp(block_confirm_interval=1, network_only=True)

        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        self.icon_service = IconService(HTTPProvider(TEST_HTTP_ENDPOINT_URI_V3))

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
            self.process_message_tx(self.icon_service, "test message")
            block_height += 1

    def _make_blocks_to_next_calculation(self) -> int:
        iiss_info = self.get_iiss_info()
        next_calculation = int(iiss_info.get('nextCalculation', 0), 16)

        self._make_blocks(to=next_calculation)

        self.assertEqual(self._get_block_height(), next_calculation)

        return next_calculation

    @staticmethod
    def create_deploy_score_tx(score_path: str, from_: 'KeyWallet',
                               to: str = SCORE_INSTALL_ADDRESS) -> 'SignedTransaction':
        transaction = DeployTransactionBuilder() \
            .from_(from_.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(DEFAULT_NID) \
            .nonce(0) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(score_path)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_)
        return signed_transaction

    @staticmethod
    def create_set_revision_tx(from_: 'KeyWallet', revision: int) -> 'SignedTransaction':
        # set revision
        transaction = CallTransactionBuilder() \
            .from_(from_.get_address()) \
            .to(GOVERNANCE_ADDRESS) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("setRevision") \
            .params({"code": revision, "name": f"1.4.{revision}"}) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_)
        return signed_transaction

    @staticmethod
    def create_transfer_icx_tx(from_: 'KeyWallet',
                               to_: str,
                               value: int,
                               step_limit: int = DEFAULT_STEP_LIMIT,
                               nid: int = DEFAULT_NID,
                               nonce: int = 0) -> 'SignedTransaction':
        transaction = TransactionBuilder() \
            .from_(from_.get_address()) \
            .to(to_) \
            .value(value) \
            .step_limit(step_limit) \
            .nid(nid) \
            .nonce(nonce) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_)
        return signed_transaction

    @staticmethod
    def create_register_prep_tx(key_wallet: 'KeyWallet',
                                reg_data: Dict[str, Union[str, bytes]] = None,
                                value: int = 0,
                                step_limit: int = DEFAULT_STEP_LIMIT,
                                nid: int = DEFAULT_NID,
                                nonce: int = 0) -> 'SignedTransaction':
        if not reg_data:
            reg_data = Base._create_register_prep_params(key_wallet)

        transaction = CallTransactionBuilder(). \
            from_(key_wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("registerPRep"). \
            params(reg_data). \
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

        return signed_transaction

    @staticmethod
    def create_unregister_prep_tx(key_wallet: 'KeyWallet',
                                  value: int = 0,
                                  step_limit: int = DEFAULT_STEP_LIMIT,
                                  nid: int = DEFAULT_NID,
                                  nonce: int = 0) -> 'SignedTransaction':

        transaction = CallTransactionBuilder(). \
            from_(key_wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("unregisterPRep"). \
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

        return signed_transaction

    @staticmethod
    def create_set_prep_tx(key_wallet: 'KeyWallet',
                           irep: int=None,
                           set_data: Dict[str, Union[str, bytes]] = None,
                           value: int = 0,
                           step_limit: int = DEFAULT_STEP_LIMIT,
                           nid: int = DEFAULT_NID,
                           nonce: int = 0) -> 'SignedTransaction':
        if set_data is None:
            set_data = {}
        if irep is not None:
            set_data[ConstantKeys.IREP] = hex(irep)

        transaction = CallTransactionBuilder(). \
            from_(key_wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setPRep"). \
            params(set_data). \
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

        return signed_transaction

    @staticmethod
    def create_set_stake_tx(key_wallet: KeyWallet,
                            stake: int,
                            value: int = 0,
                            step_limit: int = DEFAULT_STEP_LIMIT,
                            nid: int = DEFAULT_NID,
                            nonce: int = 0) -> 'SignedTransaction':

        transaction = CallTransactionBuilder(). \
            from_(key_wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setStake"). \
            params({"value": hex(stake)}). \
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

        return signed_transaction

    @staticmethod
    def create_set_delegation_tx(key_wallet: KeyWallet,
                                 delegations: List[Tuple['KeyWallet', int]],
                                 value: int = 0,
                                 step_limit: int = DEFAULT_STEP_LIMIT,
                                 nid: int = DEFAULT_NID,
                                 nonce: int = 0) -> 'SignedTransaction':
        delegations = Base.create_delegation_params(delegations)

        transaction = CallTransactionBuilder(). \
            from_(key_wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("setDelegation"). \
            params({"delegations": delegations}). \
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

        return signed_transaction

    @staticmethod
    def create_claim_iscore_tx(key_wallet: 'KeyWallet',
                               value: int = 0,
                               step_limit: int = DEFAULT_STEP_LIMIT,
                               nid: int = DEFAULT_NID,
                               nonce: int = 0) -> 'SignedTransaction':

        transaction = CallTransactionBuilder(). \
            from_(key_wallet.get_address()). \
            to(SYSTEM_ADDRESS). \
            value(value). \
            step_limit(step_limit). \
            nid(nid). \
            nonce(nonce). \
            method("claimIScore"). \
            build()

        signed_transaction = SignedTransaction(transaction, key_wallet)

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
                 key_wallet: 'KeyWallet') -> dict:

        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getPRep") \
            .params({"address": key_wallet.get_address()}) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_stake(self,
                  key_wallet: 'KeyWallet') -> dict:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getStake") \
            .params({"address": key_wallet.get_address()}) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_delegation(self,
                       key_wallet: 'KeyWallet') -> dict:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("getDelegation") \
            .params({"address": key_wallet.get_address()}) \
            .build()
        response = self.process_call(call, self.icon_service)
        return response

    def get_balance(self,
                    key_wallet: 'KeyWallet') -> dict:
        return self.icon_service.get_balance(key_wallet.get_address())

    def query_iscore(self,
                     key_wallet: 'KeyWallet') -> dict:
        call = CallBuilder() \
            .from_(self._test1.get_address()) \
            .to(SYSTEM_ADDRESS) \
            .method("queryIScore") \
            .params({"address": key_wallet.get_address()}) \
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
    def _create_register_prep_params(key_wallet: 'KeyWallet') -> Dict[str, Union[str, bytes]]:
        name = f"node{key_wallet.get_address()[2:7]}"

        return {
            ConstantKeys.NAME: name,
            ConstantKeys.EMAIL: f"node{name}@example.com",
            ConstantKeys.WEBSITE: f"https://node{name}.example.com",
            ConstantKeys.DETAILS: f"https://node{name}.example.com/details",
            ConstantKeys.P2P_END_POINT: f"https://node{name}.example.com:7100",
            ConstantKeys.PUBLIC_KEY: f"0x{key_wallet.bytes_public_key.hex()}"
        }

    @staticmethod
    def create_delegation_params(params: List[Tuple['KeyWallet', int]]) -> List[Dict[str, str]]:
        return [{"address": key_wallet.get_address(), "value": hex(value)}
                for (key_wallet, value) in params
                if value > 0]
