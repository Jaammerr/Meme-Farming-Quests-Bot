from sys import stderr

from art import tprint
from loguru import logger


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
