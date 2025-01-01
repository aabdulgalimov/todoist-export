from todoist_export.cli import parse_args


def main():
    args = parse_args()

    try:
        args.func(args)
    except (KeyboardInterrupt, EOFError):
        pass


if __name__ == "__main__":
    main()
