import os
import yaml

from loguru import logger
from models import Account, Config


def get_accounts():
    accounts_path = os.path.join(os.path.dirname(__file__), "accounts.txt")
    if not os.path.exists(accounts_path):
        logger.error(f"File <<{accounts_path}>> does not exist")
        exit(1)

    with open(accounts_path, "r") as f:
        accounts = f.readlines()

        if not accounts:
            logger.error(f"File <<{accounts_path}>> is empty")
            exit(1)

        for account in accounts:
            values = account.split("|")
            if len(values) != 2:
                logger.error(
                    f"Account <<{account}>> is not in correct format | Need to be in format: <<private_key/mnemonic|proxy>>"
                )
                exit(1)

            yield Account(
                pk_or_mnemonic=values[0].strip(),
                proxy=values[1].strip(),
            )


def load_config() -> Config:
    settings_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
    if not os.path.exists(settings_path):
        logger.error(f"File <<{settings_path}>> does not exist")
        exit(1)

    with open(settings_path, "r") as f:
        settings = yaml.safe_load(f)

    if not settings.get("eth_rpc"):
        logger.error(f"eth_rpc is not provided in settings.yaml")
        exit(1)

    if not settings.get("threads"):
        logger.error(f"threads is not provided in settings.yaml")
        exit(1)

    if not settings.get("min_snapshot_amount"):
        logger.error(f"min_snapshot_amount is not provided in settings.yaml")
        exit(1)

    if not settings.get("max_snapshot_amount"):
        logger.error(f"max_snapshot_amount is not provided in settings.yaml")
        exit(1)

    accounts = list(get_accounts())
    return Config(
        eth_rpc=settings["eth_rpc"],
        threads=settings["threads"],
        accounts=accounts,
        min_snapshot_amount=settings["min_snapshot_amount"],
        max_snapshot_amount=settings["max_snapshot_amount"],
    )
