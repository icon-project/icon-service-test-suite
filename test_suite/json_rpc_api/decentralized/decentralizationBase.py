from typing import TYPE_CHECKING, List

from iconsdk.wallet.wallet import KeyWallet

from test_suite.json_rpc_api.base import Base

if TYPE_CHECKING:
    pass


class DecentralizationBase(Base):

    def distribute_icx(self, key_wallet: 'KeyWallet', addresses: List['KeyWallet'], first_distribute_amount: int,
                       increment: int=0):
        distribute_tx_list = [self.create_transfer_icx_tx(key_wallet, wallet, first_distribute_amount + index*increment)
                              for index, wallet in enumerate(addresses)]
        tx_results = self.process_transaction_bulk(distribute_tx_list, self.icon_service)
        return tx_results

    def stake_bulk(self, wallets: List['KeyWallet'], first_stake_amount: int,
                   increment: int=0):
        stake_tx_list = [self.create_set_stake_tx(wallet, first_stake_amount + index*increment)
                         for index, wallet in enumerate(wallets)]
        tx_results = self.process_transaction_bulk(stake_tx_list, self.icon_service)
        return tx_results

    def delegate(self, key_wallet: 'KeyWallet', preps: List['KeyWallet'], first_delegate_amount: int, increment: int=0):
        if first_delegate_amount == 0 and increment == 0:
            delegation_data = []
        else:
            delegation_data = [(wallet, first_delegate_amount + index*increment)
                               for index, wallet in enumerate(preps[:10])]
        delegation_tx = self.create_set_delegation_tx(key_wallet, delegation_data)
        tx_result = self.process_transaction(delegation_tx, self.icon_service)
        return tx_result

    def register_prep_bulk(self, preps: List['KeyWallet']):
        """Do not use this method if you want register prep with specific prep data"""
        reg_tx_list = []
        for i, wallet in enumerate(preps):
            params = {
                "name": f"banana node{i}",
                "email": f"banana@banana{i}.com",
                "website": f"https://banana{i}.com",
                "details": f"https://banana{i}.com/detail{i}",
                "publicKey": f"0x{wallet.bytes_public_key.hex()}",
                "p2pEndpoint": f"123.213.123.123:71{i}"
            }
            tx = self.create_register_prep_tx(wallet, params)
            reg_tx_list.append(tx)
        tx_results = self.process_transaction_bulk(reg_tx_list, self.icon_service)
        return tx_results

    def unregister_prep_bulk(self, preps: List['KeyWallet']):
        unregister_tx_list = [self.create_unregister_prep_tx(prep) for prep in preps]
        tx_results = self.process_transaction_bulk(unregister_tx_list, self.icon_service)
        return tx_results
