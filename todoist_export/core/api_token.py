import argparse
import sys
from getpass import getpass

import keyring


KEYRING_APP_NAME = "todoist_export"
KEYRING_CRED_NAME = "api_token"


def get_token() -> str:
    token = keyring.get_password(KEYRING_APP_NAME, KEYRING_CRED_NAME)

    if not token:
        print("Todoist API token not found in the system keyring")

    return token


def show_token(args: argparse.Namespace) -> None:
    if token := get_token():
        print(token)
    else:
        sys.exit(1)


def set_token(args: argparse.Namespace = None) -> str:
    token = getpass(prompt="Enter your token: ")

    if token:
        keyring.set_password(KEYRING_APP_NAME, KEYRING_CRED_NAME, token)
        print("Token is set")
    else:
        return set_token(args)

    return token


def remove_token(args: argparse.Namespace) -> None:
    if get_token():
        keyring.delete_password(KEYRING_APP_NAME, KEYRING_CRED_NAME)
    else:
        sys.exit(1)
