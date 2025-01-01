import argparse

from todoist_export.core.export import export
from todoist_export.core.api_token import show_token, set_token, remove_token


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="todoist_export",
    )
    parser.set_defaults(func=export)
    parser.add_argument(
        "--file",
        type=str,
        metavar="PATH",
        help="path to the export file",
    )
    subparsers = parser.add_subparsers()

    # token
    token_parser = subparsers.add_parser(
        "token",
        help="manage Todoist API token",
    )
    token_subparsers = token_parser.add_subparsers(required=True)

    # token show
    token_show_parser = token_subparsers.add_parser(
        "show",
        help="show the token",
    )
    token_show_parser.set_defaults(func=show_token)

    # token set
    token_set_parser = token_subparsers.add_parser(
        "set",
        help="set a new token",
    )
    token_set_parser.set_defaults(func=set_token)

    # token remove
    token_remove_parser = token_subparsers.add_parser(
        "remove",
        help="remove the token",
    )
    token_remove_parser.set_defaults(func=remove_token)

    return parser.parse_args()
