from config import VERBOSE_LOGGING


def log(message: str):
    """
    Single print gateway for the whole project.
    To disable all terminal output by code-comment, comment the print line below.
    """
    if VERBOSE_LOGGING:
        print(message)
