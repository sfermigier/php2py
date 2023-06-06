import ast
import shlex
import subprocess
import tempfile
from ast import unparse

import rich
from devtools import debug

from php2py.parser import parse
from php2py.translator import Translator


def translate(source):
    php_ast = parse(source)
    return Translator().translate_root(php_ast)


def ast_eq(node1: ast.AST | list[ast.AST], node2: ast.AST | list[ast.AST]) -> bool:
    if type(node1) is not type(node2):
        debug(type(node1), type(node2))
        return False

    if isinstance(node1, ast.AST):
        for k, v in vars(node1).items():
            if k in ("lineno", "col_offset", "ctx"):
                continue
            v2 = getattr(node2, k)
            if not ast_eq(v, v2):
                debug(v, v2)
                return False
        return True

    elif isinstance(node1, list) and isinstance(node2, list):
        return all([ast_eq(n1, n2) for n1, n2 in zip(node1, node2)])

    else:
        return node1 == node2


def dump_php_ast(ast):
    raw = repr(ast)
    with tempfile.NamedTemporaryFile("w+", suffix=".py") as fd:
        fd.write(raw)
        fd.flush()

        cmd_line = f"black {fd.name}"
        args = shlex.split(cmd_line)
        with subprocess.Popen(
            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ) as p:
            p.wait()

        fd.seek(0)
        return print(fd.read())


def check_compiles(input, expected=""):
    php_ast = parse(input)
    try:
        py_ast = translate(input)
    except:
        rich.print("[red]Error while translating[/red]")
        print("php_ast:")
        dump_php_ast(php_ast)
        raise

    try:
        output = unparse(py_ast)
    except:
        rich.print("[red]Error while translating[/red]")
        print("php_ast:")
        dump_php_ast(php_ast)
        print("py_ast=", ast.dump(py_ast, indent=2))
        # print("py_ast=", astpretty.pprint(py_ast, indent="  "))
        raise

    output = output.strip()

    output_ast = ast.parse(output)

    if not expected:
        return

    if expected != output:
        print("php_ast:")
        dump_php_ast(php_ast)
        print("py_ast=", ast.dump(py_ast, indent=2))
        # print("py_ast=", astpretty.pprint(py_ast, indent="  "))
        debug(output)

    assert expected == output
