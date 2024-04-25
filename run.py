import asyncio
import sys

from asyncio import WindowsSelectorEventLoopPolicy
from loguru import logger

from src.bot import MemeSnapshot
from src.utils import show_dev_info, setup_logger

from loader import config, semaphore
from models import Account
from src.utils import export_accounts


async def run_safe(account: Account):
    async with semaphore:
        meme_quests = MemeSnapshot(account)
        return await meme_quests.start()


async def run():
    show_dev_info()
    logger.info(
        f"\n\nMeme Snapshot Bot started | Version: 1.0 | Total accounts: {len(config.accounts)} | Threads: {config.threads}\n\n"
    )

    tasks = [asyncio.create_task(run_safe(account)) for account in config.accounts]
    export_accounts_data = await asyncio.gather(*tasks)
    export_accounts(export_accounts_data)

    logger.info("\n\nMeme Snapshot Bot finished")


if __name__ == "__main__":
    setup_logger()

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    asyncio.run(run())
