from pydantic import BaseModel


class SignatureData(BaseModel):
    signature: str
    message: str


class P2TRBTCWallet(BaseModel):
    mnemonic: str
    address: str
    path: str = "m/86'/0'/0'/0/7"
