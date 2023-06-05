#!/usr/bin/env python3
import sys
from ast import unparse

from .parser import install_parser, parse
from .translator import Translator


def main(source_file):
    install_parser()

    php_ast = parse(open(source_file).read())
    translator = Translator()
    py_ast = translator.translate(php_ast)
    output = unparse(py_ast)
    print(output)


if __name__ == "__main__":
    main(sys.argv[1])
