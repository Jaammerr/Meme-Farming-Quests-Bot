import asyncio
import os
import aiofiles
import pyuseragents

from typing import Literal
from loguru import logger
from web3 import Web3, Account

from curl_cffi.requests import AsyncSession
from models import Account as MemeAccount, QuestResult, QuestsList
from twitter_api import Account as TwitterAccount
from twitter_api.models import BindAccountParamsV1

from loader import config
from .wallet import Wallet
from .exceptions.base import MemeError

Account.enable_unaudited_hdwallet_features()


class MemeQuests:
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

    async def wallet_info(self):
        response = await self.send_request(
            request_type="GET", method=f"/wallet/info/{self.address}"
        )
        print(response)

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

    async def complete_connect_quest(self) -> QuestResult:
        response = await self.send_request(
            request_type="POST", method="/farming/quest/connect"
        )
        return QuestResult(**response)

    async def get_quests(self) -> QuestsList:
        response = await self.send_request(request_type="GET", method="/farming/quests")
        return QuestsList(**response)

    async def complete_quest(self, quest_id: int, quest_type: str) -> QuestResult:
        response = await self.send_request(
            request_type="POST",
            method=f"/farming/quest/{quest_type}",
            json_data={"questId": quest_id},
        )
        return QuestResult(**response)

    async def process_sleep(self):
        logger.debug(
            f"Account: {self.address} | Waiting for {config.delay_between_quests} sec..."
        )
        await asyncio.sleep(config.delay_between_quests)

    async def complete_quests(self):
        quests = await self.get_quests()
        for quest in quests.quests:

            while True:
                try:
                    if quest.id == 1:
                        quest_result = await self.complete_connect_quest()
                    else:
                        quest_result = await self.complete_quest(quest.id, quest.type)

                    logger.success(
                        f"Account: {self.address} | Quest completed: {quest.name} | Earned: {quest_result.earned} | Steaks: {quest_result.steaks.total}"
                    )
                    break

                except MemeError as error:
                    if error.error_message() == "not_found":
                        logger.warning(
                            f"Account: {self.address} | Quest failed: {quest.name} | Meme Error: {error.error_message()} | Retrying.."
                        )
                        await self.process_sleep()

                    else:
                        logger.error(
                            f"Account: {self.address} | Quest failed: {quest.name} | Meme Error: {error.error_message()} | Skipped..."
                        )
                        break

                except Exception as error:
                    logger.error(
                        f"Account: {self.address} | Quest failed: {quest.name} | Unknown Error: {error} | Retrying.."
                    )
                    await self.process_sleep()

            await self.process_sleep()

        # logger.success(f"Account: {self.address} | All quests completed successfully")

    async def bind_twitter(self) -> bool:
        for _ in range(3):
            try:
                bind_url = "https://memestaking-api.stakeland.com/farming/twitter/auth?callback=https://www.stakeland.com/farming"
                account = TwitterAccount.run(
                    auth_token=self.account.auth_token, proxy=self.account.proxy
                )

                bind_data = BindAccountParamsV1(url=bind_url)
                bound_data = account.bind_account_v1(bind_data)

                json_data = {
                    "oauth_token": bound_data.oauth_token,
                    "oauth_verifier": bound_data.oauth_verifier,
                }

                response = await self.send_request(
                    request_type="POST",
                    method="/farming/twitter/auth",
                    json_data=json_data,
                    verify=False,
                )

                if not response["success"]:
                    if response.get("error") != "already_bound":
                        raise Exception(
                            f"Failed to bind twitter account | Error: {response.get('error')}"
                        )
                    logger.warning(
                        f"Account: {self.address} | Twitter account already bound"
                    )
                else:
                    logger.success(
                        f"Account: {self.address} | Twitter account bound successfully"
                    )

                await self.process_sleep()
                return True

            except Exception as error:
                logger.error(
                    f"Account: {self.address} | Failed to bind twitter account | Error: {error} | Retrying.."
                )
                await self.process_sleep()

        logger.error(
            f"Account: {self.address} | Failed to bind twitter account | Max retries exceeded"
        )
        return False

    async def export_account(self, success: bool = True) -> None:
        if success:
            logger.info(f"Account: {self.address} | Finished successfully")
            accounts_path = os.path.join(
                os.getcwd().replace("//src", ""), "config", "success_accounts.txt"
            )
        else:
            logger.info(f"Account: {self.address} | Finished with error")
            accounts_path = os.path.join(
                os.getcwd().replace("//src", ""), "config", "failed_accounts.txt"
            )

        async with aiofiles.open(accounts_path, "a") as file:
            await file.write(
                f"{self.account.auth_token}|{self.account.pk_or_mnemonic}|{self.get_proxy}\n"
            )

    async def start(self) -> None:
        try:
            if not await self.auth():
                return await self.export_account(success=False)

            if not await self.bind_twitter():
                return await self.export_account(success=False)

            await self.complete_quests()
            return await self.export_account(success=True)

        except Exception as error:
            logger.error(f"Account: {self.address} | Unknown error | Error: {error}")
            return await self.export_account(success=False)
