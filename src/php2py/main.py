#!/usr/bin/env python3

import sys
import traceback
from ast import unparse
from pathlib import Path

from cleez.colors import blue, red

from .parser import install_parser, parse
from .translator import Translator


def main(source_files, ignore_errors):
    install_parser()

    for source_file in source_files:
        print(blue(f"Transpiling {source_file}..."))

        try:
            php_ast = parse(open(source_file).read())
            translator = Translator()
            py_ast = translator.translate(php_ast)
            output = unparse(py_ast)
            Path(source_file).with_suffix(".py").write_text(output)
        except (NotImplementedError, KeyError) as e:
            print(red("Error transpiling file."))
            print(e)
            traceback.print_exc()
            print()
            if not ignore_errors:
                sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
