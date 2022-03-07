import ast
from ast import unparse, dump

from devtools import debug

from php2py.parser import parse
from php2py.translator import Translator


def translate(source):
    ast = parse(source)
    return Translator().translate_root(ast)


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


# def test_assign1():
#     input = r"""<?php
#         $a = 1;
#         $b = +2;
#         $c = -3;
#     ?>"""
#     py_ast = translate(input)
#     debug(py_ast)
#     debug(dump(py_ast))
#     output = unparse(py_ast)
#     debug(output)
#     assert False


def test_echo():
    input = '<?php echo "hello, world!"; ?>'

    py_ast = translate(input)
    expected_ast = ast.Module(
        body=[
            ast.Call(
                func=ast.Name(id="echo", ctx=ast.Load()),
                args=[ast.Constant(value="hello, world!")],
                keywords=[],
            )
        ],
        type_ignores=[],
    )
    assert ast_eq(expected_ast, py_ast)

    output = unparse(py_ast)
    expected = "echo('hello, world!')"
    assert output == expected
