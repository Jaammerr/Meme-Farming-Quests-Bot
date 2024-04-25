from loguru import logger
from pydantic import BaseModel, field_validator, HttpUrl, PositiveInt


class Account(BaseModel):
    pk_or_mnemonic: str
    proxy: str

    @field_validator("proxy", mode="before")
    def check_proxy(cls, value) -> str:
        proxy_values = value.split(":")
        if len(proxy_values) != 4:
            logger.error(
                f"Proxy <<{value}>> is not in correct format | Need to be in format: <<ip:port:username:password>>"
            )
            exit(1)

        proxy_url = f"http://{proxy_values[2]}:{proxy_values[3]}@{proxy_values[0]}:{proxy_values[1]}"
        return proxy_url


class Config(BaseModel):
    eth_rpc: HttpUrl
    threads: PositiveInt
    min_snapshot_amount: PositiveInt
    max_snapshot_amount: PositiveInt
    accounts: list[Account]



class ExportAccountData(BaseModel):
    success: bool
    pk_or_mnemonic: str
    proxy: str
