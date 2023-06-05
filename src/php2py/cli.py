import argparse


def cli():
    # Set up the parser
    parser = argparse.ArgumentParser(description="PHP to Python transpiler.")

    subparsers = parser.add_subparsers(help="sub-command help")

    update_parser = subparsers.add_parser("update", help="Update the PHP parser")
    update_parser.set_defaults(func=run_update)

    convert_parser = subparsers.add_parser(
        "convert", help="Convert (compile) a PHP file to Python"
    )
    convert_parser.add_argument("file")
    convert_parser.set_defaults(func=run_convert)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def run_convert(args):
    from php2py.main import main

    main(args.file)


def run_update(args):
    from php2py.parser import install_parser

    install_parser(force=True)
