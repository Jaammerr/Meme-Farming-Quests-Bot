import asyncio
import random
import pyuseragents

from typing import Literal
from loguru import logger
from web3 import Web3, Account

from curl_cffi.requests import AsyncSession
from models import Account as MemeAccount, ExportAccountData

from loader import config
from .wallet import Wallet
from .exceptions.base import MemeError

Account.enable_unaudited_hdwallet_features()


class MemeSnapshot:
    API_URL = "https://memestaking-api.stakeland.com"

    def __init__(self, account: MemeAccount):
        super().__init__()
        self.account = account
        self.session = self.setup_session()
        self.web3 = Web3(Web3.HTTPProvider(config.eth_rpc))

        self.wallet = Wallet(account.pk_or_mnemonic)

    @property
    def address(self) -> str:
        return self.wallet.address

    @property
    def get_proxy(self) -> str:
        values = self.account.proxy.replace("http://", "").replace("@", ":").split(":")
        proxy_str = f"{values[2]}:{values[3]}:{values[0]}:{values[1]}"
        return proxy_str

    def setup_session(self):
        session = AsyncSession()
        session.headers = {
            "authority": "memestaking-api.stakeland.com",
            "accept": "application/json",
            "accept-language": "fr-FR,fr;q=0.9",
            "origin": "https://www.stakeland.com",
            "user-agent": pyuseragents.random(),
        }
        session.proxies = {
            "http": self.account.proxy,
            "https": self.account.proxy,
        }
        session.verify = False

        return session

    async def send_request(
        self,
        request_type: Literal["POST", "GET"] = "POST",
        method: str = None,
        json_data: dict = None,
        params: dict = None,
        url: str = None,
        verify: bool = True,
    ):
        def _verify_response(_response: dict) -> dict:
            if "success" in _response:
                if not _response["success"]:
                    raise MemeError({"error_message": _response.get("error")})

            return _response

        if request_type == "POST":
            if not url:
                response = await self.session.post(
                    f"{self.API_URL}{method}", json=json_data, params=params
                )

            else:
                response = await self.session.post(url, json=json_data, params=params)

        else:
            if not url:
                response = await self.session.get(
                    f"{self.API_URL}{method}", params=params
                )

            else:
                response = await self.session.get(url, params=params)

        response.raise_for_status()
        if verify:
            return _verify_response(response.json())
        return response.json()

    async def wallet_info(self) -> dict:
        response = await self.send_request(
            request_type="GET", method=f"/wallet/info/{self.address}"
        )
        return response

    async def auth(self) -> bool:
        for _ in range(3):
            try:
                signature_data = self.wallet.get_signature_data()

                json_data = {
                    "address": self.address,
                    "message": signature_data.message,
                    "signature": signature_data.signature,
                }

                response = await self.send_request(
                    request_type="POST", method="/wallet/auth", json_data=json_data
                )
                if not response.get("accessToken"):
                    raise Exception("Auth failed")

                self.session.headers["authorization"] = (
                    f"Bearer {response['accessToken']}"
                )
                logger.success(f"Account: {self.address} | Authenticated successfully")
                await self.process_sleep()
                return True

            except Exception as error:
                logger.error(
                    f"Account: {self.address} | Failed to authenticate | Error: {error} | Retrying.."
                )
                await self.process_sleep()

        logger.error(
            f"Account: {self.address} | Failed to authenticate | Max retries exceeded"
        )


    async def process_sleep(self):
        delay = random.randint(1, 5)
        logger.debug(
            f"Account: {self.address} | Waiting for {delay} sec..."
        )
        await asyncio.sleep(delay)

    async def get_snapshot_amount(self) -> float:
        response = await self.wallet_info()
        balance = float(response["steaks"]["total"])

        percentage_of_snapshot = random.randint(
            config.min_snapshot_amount, config.max_snapshot_amount
        )

        snapshot_amount = balance * (percentage_of_snapshot / 100)
        logger.info(f"Account: {self.address} | Snapshot amount: {snapshot_amount} STEAKS | {percentage_of_snapshot}%")
        return snapshot_amount

    async def snapshot(self) -> bool:
        snapshot_amount = await self.get_snapshot_amount()
        json_data = {
            "id": 1,
            "amount": str(snapshot_amount),
        }

        for _ in range(3):
            try:
                await self.send_request(
                    request_type="POST", method="/wallet/allocation", json_data=json_data
                )
                logger.success(f"Account: {self.address} | Snapshot successful")
                return True

            except Exception as error:
                logger.error(
                    f"Account: {self.address} | Failed to snapshot | Error: {error} | Retrying.."
                )
                await self.process_sleep()

        logger.error(f"Account: {self.address} | Failed to snapshot | Max retries exceeded")
        return False

    async def export_account(self, success: bool = True) -> ExportAccountData:
        if success:
            logger.info(f"Account: {self.address} | Finished successfully")
            return ExportAccountData(
                success=True,
                pk_or_mnemonic=self.account.pk_or_mnemonic,
                proxy=self.get_proxy,
            )

        else:
            logger.info(f"Account: {self.address} | Finished with error")
            return ExportAccountData(
                success=False,
                pk_or_mnemonic=self.account.pk_or_mnemonic,
                proxy=self.get_proxy,
            )


    async def start(self) -> ExportAccountData:
        try:
            if not await self.auth():
                return await self.export_account(success=False)

            if not await self.snapshot():
                return await self.export_account(success=False)

            return await self.export_account(success=True)

        except Exception as error:
            logger.error(f"Account: {self.address} | Unknown error | Error: {error}")
            return await self.export_account(success=False)
