from sys import stderr

from art import tprint
from loguru import logger

from models import ExportAccountData


def show_dev_info():
    tprint("JamBit")
    print("\033[36m" + "VERSION: " + "\033[34m" + "1.0" + "\033[34m")
    print("\033[36m" + "Channel: " + "\033[34m" + "https://t.me/JamBitPY" + "\033[34m")
    print(
        "\033[36m"
        + "GitHub: "
        + "\033[34m"
        + "https://github.com/Jaammerr"
        + "\033[34m"
    )
    print(
        "\033[36m"
        + "DONATION EVM ADDRESS: "
        + "\033[34m"
        + "0x08e3fdbb830ee591c0533C5E58f937D312b07198"
        + "\033[0m"
    )
    print()


def setup_logger():
    logger.remove()
    logger.add(
        stderr,
        format="<white>{time:HH:mm:ss}</white>"
        " | <bold><level>{level: <7}</level></bold>"
        " | <cyan>{line: <3}</cyan>"
        " | <white>{message}</white>",
    )
    logger.add("logs/debug.log", level="DEBUG", rotation="1 week", compression="zip")



def export_accounts(accounts: tuple[ExportAccountData]) -> None:
    success_accounts = open("./config/success_accounts.txt", "a")
    failed_accounts = open("./config/failed_accounts.txt", "a")

    for account in accounts:
        account_data = f"{account.auth_token}|{account.pk_or_mnemonic}|{account.proxy}" if not account.ordinal_mnemonic else f"{account.auth_token}|{account.pk_or_mnemonic}|{account.proxy}|{account.ordinal_mnemonic}:{account.ordinal_address}"

        if account.success:
            success_accounts.write(account_data + "\n")
        else:
            failed_accounts.write(account_data + "\n")

    success_accounts.close()
    failed_accounts.close()

    logger.debug("Accounts results exported")

