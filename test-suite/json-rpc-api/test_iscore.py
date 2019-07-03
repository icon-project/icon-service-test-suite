import os

from iconsdk.builder.transaction_builder import CallTransactionBuilder, TransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from tbears.libs.icon_integrate_test import IconIntegrateTestBase

DIR_PATH = os.path.abspath(os.path.dirname(__file__))
min_rrep = 200
min_delegation = 788400
block_per_year = 15768000
gv_divider = 10000
iscore_multiplier = 1000
reward_divider = block_per_year * gv_divider / iscore_multiplier


class TestIScore(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))
    SYSTEM_ADDRESS = "cx0000000000000000000000000000000000000000"
    MIN_DELEGATION = 788_400

    def setUp(self):
        super().setUp(block_confirm_interval=1, network_only=True)

        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

    def _make_account(self, balance: int = 0, check_result: bool = True) -> 'KeyWallet':
        # create account
        account: 'KeyWallet' = KeyWallet.create()

        if balance == 0:
            return account

        # Generates an instance of transaction for sending icx.
        transaction = TransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(account.get_address()) \
            .value(balance) \
            .step_limit(1000000) \
            .nid(3) \
            .nonce(100) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        if check_result:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

        return account

    def _call_transaction(self, _from: 'KeyWallet', to: str, method: str, params: dict = {},
                          check_result: bool = True) -> dict:
        # Generates a 'setStake' instance of transaction
        transaction = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(to) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method(method) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, _from)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        if check_result:
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

        return tx_result

    def _call(self, to: str, method: str, params: dict) -> dict:
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(to) \
            .method(method) \
            .params(params) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)

        return response

    def _get_block_height(self) -> int:
        block = self.icon_service.get_block("latest")
        return block['height']

    def _make_blocks(self, to: int):
        block_height = self._get_block_height()

        while to > block_height:
            self.process_message_tx(self.icon_service, "test message")
            block_height += 1

    def _make_blocks_to_next_calculation(self) -> int:
        iiss_info = self._get_iiss_info()
        next_calculation = int(iiss_info.get('nextCalculation', 0), 16)

        self._make_blocks(to=next_calculation)

        self.assertEqual(self._get_block_height(), next_calculation)

        return next_calculation

    def _get_iiss_info(self):
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method='getIISSInfo',
                              params={})
        return response

    def _calculate_iscore(self, delegation, from_, to) -> int:
        if delegation < min_delegation:
            return 0

        iiss_info = self._get_iiss_info()
        rrep = int(iiss_info['variable'].get('rrep'), 16)
        if rrep < min_rrep:
            return 0

        # iscore = delegation_amount * period * rrep / reward_divider
        return int(delegation * rrep * (to - from_) / reward_divider)

    def test_iscore(self):
        stake_value: int = self.MIN_DELEGATION * 1000
        delegation_value: int = self.MIN_DELEGATION * 100
        account = self._make_account(stake_value)
        prep = self._test1

        # register P-Rep
        self._call_transaction(_from=prep,
                               to=self.SYSTEM_ADDRESS,
                               method="registerPRep",
                               params={"name": "prep_test",
                                       "email": "prep_test@test.com",
                                       "website": "https://prep_test.com",
                                       "details": "https://detail.prep_test.com",
                                       "p2pEndPoint": "target://prep_test.com:7100",
                                       "publicKey": f'0x{prep.bytes_public_key.hex()}'
                               },
                               check_result=False)

        # setStake
        self._call_transaction(_from=account,
                               to=self.SYSTEM_ADDRESS,
                               method="setStake",
                               params={"value": hex(stake_value)})


        # getStake
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method="getStake",
                              params={"address": account.get_address()})

        expect_result = {
            "stake": hex(stake_value),
        }
        self.assertEqual(expect_result, response)

        # delegate to P-Rep
        delegation_params = {
            "delegations": [
                {
                    "address": prep.get_address(),
                    "value": hex(delegation_value)
                }
            ]
        }
        tx_result = self._call_transaction(_from=account,
                               to=self.SYSTEM_ADDRESS,
                               method="setDelegation",
                               params=delegation_params)
        delegation_block = tx_result['blockHeight']

        # query delegation
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method="getDelegation",
                              params={"address": account.get_address()})

        expect_result = {
            "totalDelegated": hex(delegation_value),
            "votingPower": hex(stake_value - delegation_value)
        }
        expect_result.update(delegation_params)
        self.assertEqual(expect_result, response)

        # queryIScore
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method="queryIScore",
                              params={"address": account.get_address()})
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to 1st calculation
        calculate1_block_height = self._make_blocks_to_next_calculation()
        # calculate IScore with rrep at calculate1_block_height
        iscore1 = self._calculate_iscore(delegation_value, delegation_block, calculate1_block_height)

        # queryIScore
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method="queryIScore",
                              params={"address": account.get_address()})
        self.assertEqual(hex(0), response['iscore'])

        # increase block height to 2nd calculation
        calculate2_block_height = self._make_blocks_to_next_calculation()
        iscore2 = self._calculate_iscore(delegation_value, calculate1_block_height, calculate2_block_height)

        # queryIScore
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method="queryIScore",
                              params={"address": account.get_address()})
        self.assertEqual(hex(iscore1), response['iscore'])
        self.assertEqual(hex(calculate1_block_height), response['blockHeight'])

        # increase block height to 3rd calculation
        calculate3_block_height = self._make_blocks_to_next_calculation()
        iscore3 = self._calculate_iscore(delegation_value, calculate2_block_height, calculate3_block_height)

        # queryIScore
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method="queryIScore",
                              params={"address": account.get_address()})
        self.assertEqual(hex(iscore1 + iscore2), response['iscore'])
        self.assertEqual(hex(calculate2_block_height), response['blockHeight'])

        # claimIScore
        self._call_transaction(_from=account,
                               to=self.SYSTEM_ADDRESS,
                               method="claimIScore",
                               params={})

        # queryIScore
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method="queryIScore",
                              params={"address": account.get_address()})
        iscore_after_claim = (iscore1 + iscore2) % 1000
        self.assertEqual(hex(iscore_after_claim), response['iscore'])
        self.assertEqual(hex(calculate2_block_height), response['blockHeight'])

        # increase block height to 4th calculation
        self._make_blocks_to_next_calculation()

        # queryIScore
        response = self._call(to=self.SYSTEM_ADDRESS,
                              method="queryIScore",
                              params={"address": account.get_address()})
        self.assertEqual(hex(iscore_after_claim + iscore3), response['iscore'])
        self.assertEqual(hex(calculate3_block_height), response['blockHeight'])
