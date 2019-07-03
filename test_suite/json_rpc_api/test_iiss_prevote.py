# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List
import unittest

from iconsdk.builder.transaction_builder import TransactionBuilder
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from .base import Base


def icx_to_loop(icx: int) -> int:
    return icx * 10 ** 18


class TestIISSPreVote(Base):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    def setUp(self):
        super().setUp()

        self.prep_wallets: List['KeyWallet'] = self._create_key_wallets(200)
        self.user_wallets: List['KeyWallet'] = self._create_key_wallets(10)

    def tearDown(self):
        super().tearDown()

    def test(self):
        init_balance: int = icx_to_loop(10000)

        self._init_accounts(self.prep_wallets, value=init_balance)
        self._init_accounts(self.user_wallets, value=init_balance)

        self._check_balance(self.prep_wallets, value=init_balance)
        self._check_balance(self.user_wallets, value=init_balance)

    def _init_accounts(self, wallets: List['KeyWallet'], value: int):
        for wallet in wallets:
            tx: 'SignedTransaction' = self.create_transfer_icx_tx(self._test1, wallet.address, value)
            tx_result: dict = self.process_transaction(tx, self.icon_service)
            self.assertTrue('status' in tx_result)
            self.assertEqual(1, tx_result['status'])

    def _check_balance(self, wallets: List['KeyWallet'], value: int):
        for wallet in wallets:
            balance: int = self.get_balance(wallet)
            self.assertEqual(value, balance)

    def _register_prep(self):
        for wallet in self.prep_wallets:
            self.create_register_prep_tx()

    @staticmethod
    def _create_key_wallets(size: int) -> List['KeyWallet']:
        return [KeyWallet.create() for _ in range(size)]

    def _test(self):
        print("_test")
