from pydantic import BaseModel


class SignatureData(BaseModel):
    signature: str
    message: str
