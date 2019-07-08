import os

from iconsdk.signed_transaction import SignedTransaction
from iconservice.icon_constant import REV_IISS

from .json_rpc_api.base import Base, GOVERNANCE_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

GOVERNANCE_SCORES = [
    '769282ab3dee78378d7443fe6c1344c76e718734e7f581961717f12a121a2be8',
    '83537e56c647fbf0b726286ee08d31f12dba1bf7e50e8119eaffbf48004f237f'
]


class TestInit(Base):

    def setUp(self):
        super().setUp()

    def test_init(self):
        # deploy governance SCORE
        for score in GOVERNANCE_SCORES:
            score_path = os.path.abspath(os.path.join(DIR_PATH, f'./data/{score}.zip'))
            tx = self.create_deploy_score_tx(score_path, self._test1, GOVERNANCE_ADDRESS)
            self.process_transaction(tx, self.icon_service)

        tx: 'SignedTransaction' = self.create_set_revision_tx(self._test1, REV_IISS)
        tx_result: dict = self.process_transaction(tx, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(True, tx_result['status'])
