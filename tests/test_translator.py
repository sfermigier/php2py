import ast
import traceback
from ast import dump, unparse

import rich
from devtools import debug

from php2py.parser import parse
from php2py.php_ast import Stmt_InlineHTML, Stmt_Nop
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


def check_compiles(input, expected):
    php_ast = parse(input)
    try:
        py_ast = translate(input)
    except:
        rich.print("[red]Error while translating[/red]")
        debug(php_ast)
        traceback.print_exc()
        raise

    output = unparse(py_ast)

    if expected != output:
        debug(php_ast)
        print("py_ast=", dump(py_ast, indent=2))
        debug(output)

    assert expected == output


def test_inline_html():
    input = "html <?php // php ?> more html"
    php_ast = parse(input)
    expected = [
        Stmt_InlineHTML(value="html "),
        Stmt_Nop(),
        Stmt_InlineHTML(value=" more html"),
    ]
    assert php_ast == expected
    # TODO

    # check_compiles(input, expected)


def test_expressions():
    input = "<?php 1; 1.2; 'toto'; +1; -1; 1+2; 2-1; 3*6; 4/2; ?>"
    expected = (
        "1\n" "1.2\n" "'toto'\n" "+1\n" "-1\n" "1 + 2\n" "2 - 1\n" "3 * 6\n" "4 / 2"
    )
    check_compiles(input, expected)


def test_exit():
    input = "<?php exit; exit(); exit(123); die; die(); die(456); ?>"
    expected = (
        "\n"
        "raise SystemExit()\n"
        "\n"
        "raise SystemExit()\n"
        "\n"
        "raise SystemExit(123)\n"
        "\n"
        "raise SystemExit()\n"
        "\n"
        "raise SystemExit()\n"
        "\n"
        "raise SystemExit(456)"
    )
    check_compiles(input, expected)


# def test_isset():
#     input = r"""<?php
#         isset($a);
#         isset($b->c);
#         isset($d['e']);
#         isset($f, $g);
#         isset($h->m()['i1']['i2']);
#     ?>"""
#     expected = ""
#     check_compiles(input, expected)


def test_assign():
    input = r"""<?php
        $a = 1;
        $b = +2;
        $c = -3;
    ?>"""
    expected = "\n" "a = 1\n" "\n" "b = +2\n" "\n" "c = -3"
    check_compiles(input, expected)


def test_assign2():
    input = r"""<?php
        $c = !$d;
        $e = ~$f;
    ?>"""
    expected = "\n" "c = not d\n" "\n" "e = ~f"
    check_compiles(input, expected)


def test_constants():
    input = r"""<?php
        $a = true;
        $b = TRUE;
        $c = false;
        $d = False;
        $e = Null;
    ?>"""
    expected = (
        "\n"
        "a = True\n"
        "\n"
        "b = True\n"
        "\n"
        "c = False\n"
        "\n"
        "d = False\n"
        "\n"
        "e = None"
    )
    check_compiles(input, expected)


def test_echo():
    input = '<?php echo "hello, world!"; ?>'
    expected = "echo('hello, world!')"
    check_compiles(input, expected)


def test_string_unescape():
    # TODO: check this is correct
    input = r"""<?php "\r\n\t" ?>"""
    expected = '"""\\r\n\t"""'
    check_compiles(input, expected)

    # input = r"""<?php '\r\n\t' ?>"""
    # expected = '"""\\r\\n\\t"""'
    # check_compiles(input, expected)


def xxtest_object_properties():
    input = r"""<?php
        $object->property;
        # $object->foreach;
        # $object->$variable;
        # $object->$variable->schmariable;
        # $object->$variable->$schmariable;
    ?>"""
    expected = ""
    check_compiles(input, expected)
