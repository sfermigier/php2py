#!/usr/bin/env python3
import subprocess
from ast import unparse
from pathlib import Path

import click
from icecream import install

from php2py.parser import parse
from php2py.translator import Translator

install()

TEMP_DIR = Path("/tmp/php2py")
PHP_PARSE = TEMP_DIR / "vendor/nikic/php-parser/bin/php-parse"


@click.command()
@click.argument("source_file")
def main(source_file):
    install_parser()

    php_ast = parse(open(source_file).read(), php_parse=PHP_PARSE)
    translator = Translator()
    py_ast = translator.translate(php_ast)
    output = unparse(py_ast)
    print(output)


def install_parser():
    if Path(PHP_PARSE).exists():
        return

    Path(TEMP_DIR).mkdir(exist_ok=True)

    etc_dir = Path(__file__).parent / "etc"
    print(etc_dir)
    for file in etc_dir.glob("*"):
        dest = Path(TEMP_DIR) / file.name
        print(dest)
        if dest.exists():
            continue
        dest.write_text(file.read_text())

    subprocess.run("composer install", shell=True, cwd=TEMP_DIR)


if __name__ == "__main__":
    main()
