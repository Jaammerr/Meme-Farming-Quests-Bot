from embit import bip32, script
from embit.networks import NETWORKS
from eth_account.messages import encode_defunct
from mnemonic import Mnemonic
from web3 import Web3, Account

from models import SignatureData, P2TRBTCWallet
from loader import config


Account.enable_unaudited_hdwallet_features()


class Wallet:
    def __init__(self, pk_or_mnemonic: str):
        self.web3 = Web3(Web3.HTTPProvider(config.eth_rpc))
        if pk_or_mnemonic.startswith("0x"):
            self.wallet = self.web3.eth.account.from_key(pk_or_mnemonic)
        else:
            self.wallet = self.web3.eth.account.from_mnemonic(pk_or_mnemonic)

    @property
    def address(self) -> str:
        return self.wallet.address

    @property
    def sign_message(self) -> str:
        return f"This wallet will be used for farming.\n\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\n\nWallet: {self.address[:5]}...{self.address[-4:]}"

    def get_signature_data(self) -> SignatureData:
        encoded_message = encode_defunct(text=self.sign_message)
        signed_message = self.wallet.sign_message(encoded_message)
        return SignatureData(
            signature=signed_message.signature.hex(), message=self.sign_message
        )


    @staticmethod
    def generate_p2tr_wallet() -> P2TRBTCWallet:
        mnemo = Mnemonic("english")
        mnemonic = mnemo.generate(strength=256)
        seed = mnemo.to_seed(mnemonic)

        taproot_derivation_path = f"m/86'/0'/0'/0/0"
        root = bip32.HDKey.from_seed(seed, version=b"\x04\x88\xad\xe4")
        network = NETWORKS["main"]

        taproot_key = root.derive(taproot_derivation_path)
        taproot_script_pubkey = script.p2tr(taproot_key)
        taproot_address = taproot_script_pubkey.address(network)

        return P2TRBTCWallet(
            mnemonic=mnemonic,
            address=taproot_address,
        )
