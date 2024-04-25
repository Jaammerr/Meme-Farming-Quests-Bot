from eth_account.messages import encode_defunct
from web3 import Web3, Account

from models import SignatureData
from loader import config


Account.enable_unaudited_hdwallet_features()


class Wallet:
    def __init__(self, pk_or_mnemonic: str):
        self.web3 = Web3(Web3.HTTPProvider(config.eth_rpc))
        self.wallet = self.web3.eth.account.from_mnemonic(pk_or_mnemonic) if len(pk_or_mnemonic.split()) in (12, 24) else self.web3.eth.account.from_key(pk_or_mnemonic)

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
