import os

from typing import TYPE_CHECKING
from iconsdk.signed_transaction import SignedTransaction
from iconservice.icon_constant import REV_IISS

from .json_rpc_api.base import Base, GOVERNANCE_ADDRESS

if TYPE_CHECKING:
    from test_suite.json_rpc_api.base import Account

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

GOVERNANCE_SCORES = [
    '769282ab3dee78378d7443fe6c1344c76e718734e7f581961717f12a121a2be8',
    '83537e56c647fbf0b726286ee08d31f12dba1bf7e50e8119eaffbf48004f237f'
]


class TestInit(Base):

    def setUp(self):
        super().setUp()

    def test_init(self):
        admin: 'Account' = self.load_admin()
        # deploy governance SCORE
        for score in GOVERNANCE_SCORES:
            score_path = os.path.abspath(os.path.join(DIR_PATH, f'./data/{score}.zip'))
            tx = self.create_deploy_score_tx(score_path, admin, GOVERNANCE_ADDRESS)
            tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
            self.process_confirm_block_tx(self.icon_service, 50.0)
            tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
            for tx_result in tx_results:
                self.assertEqual(True, tx_result['status'])

        tx: 'SignedTransaction' = self.create_set_revision_tx(admin, REV_IISS)
        tx_hashes: list = self.process_transaction_without_txresult(tx, self.icon_service)
        self.process_confirm_block_tx(self.icon_service, self.sleep_ratio_from_account([admin]))
        tx_results: list = self.get_txresults(self.icon_service, tx_hashes)
        for tx_result in tx_results:
            self.assertEqual(True, tx_result['status'])
