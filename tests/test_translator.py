import ast
from ast import dump, unparse

from devtools import debug

from php2py.parser import parse
from php2py.php_ast import (
    Expr_ArrayDimFetch,
    Expr_Exit,
    Expr_Isset,
    Expr_MethodCall,
    Expr_PropertyFetch,
    Expr_Variable,
    Identifier,
    Scalar_LNumber,
    Scalar_String,
    Stmt_Expression,
    Stmt_InlineHTML,
    Stmt_Nop,
)
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


def check_compiles(input, expected):
    php_ast = parse(input)
    py_ast = translate(input)
    output = unparse(py_ast)

    if expected != output:
        print("php_ast=")
        print(php_ast)
        print("py_ast=")
        print(dump(py_ast, indent=2))

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


def test_exit():
    input = "<?php exit; exit(); exit(123); die; die(); die(456); ?>"
    php_ast = parse(input)
    expected = [
        Stmt_Expression(expr=Expr_Exit(expr=None)),
        Stmt_Expression(expr=Expr_Exit(expr=None)),
        Stmt_Expression(expr=Expr_Exit(expr=Scalar_LNumber(value=123))),
        Stmt_Expression(expr=Expr_Exit(expr=None)),
        Stmt_Expression(expr=Expr_Exit(expr=None)),
        Stmt_Expression(expr=Expr_Exit(expr=Scalar_LNumber(value=456))),
    ]
    assert php_ast == expected

    py_ast = translate(input)
    output = unparse(py_ast)
    expected = (
        "raise SystemExit()\n"
        "raise SystemExit()\n"
        "raise SystemExit(123)\n"
        "raise SystemExit()\n"
        "raise SystemExit()\n"
        "raise SystemExit(456)"
    )
    check_compiles(input, expected)

    assert output == expected


def test_isset():
    input = r"""<?php
        isset($a);
        isset($b->c);
        isset($d['e']);
        isset($f, $g);
        isset($h->m()['i1']['i2']);
    ?>"""
    expected = ""
    check_compiles(input, expected)

    php_ast = parse(input)
    expected = [
        Stmt_Expression(expr=Expr_Isset(vars=[Expr_Variable(name="a")])),
        Stmt_Expression(
            expr=Expr_Isset(
                vars=[
                    Expr_PropertyFetch(
                        var=Expr_Variable(name="b"), name=Identifier(name="c")
                    )
                ]
            )
        ),
        Stmt_Expression(
            expr=Expr_Isset(
                vars=[
                    Expr_ArrayDimFetch(
                        var=Expr_Variable(name="d"), dim=Scalar_String(value="e")
                    )
                ]
            )
        ),
        Stmt_Expression(
            expr=Expr_Isset(vars=[Expr_Variable(name="f"), Expr_Variable(name="g")])
        ),
        Stmt_Expression(
            expr=Expr_Isset(
                vars=[
                    Expr_ArrayDimFetch(
                        var=Expr_ArrayDimFetch(
                            var=Expr_MethodCall(
                                var=Expr_Variable(name="h"),
                                name=Identifier(name="m"),
                                args=[],
                            ),
                            dim=Scalar_String(value="i1"),
                        ),
                        dim=Scalar_String(value="i2"),
                    )
                ]
            )
        ),
    ]

    debug(php_ast)
    assert php_ast == expected

    # expected = [
    #     IsSet([Variable("$a")]),
    #     IsSet([ObjectProperty(Variable("$b"), "c")]),
    #     IsSet([ArrayOffset(Variable("$d"), "e")]),
    #     IsSet([Variable("$f"), Variable("$g")]),
    #     IsSet(
    #         [ArrayOffset(ArrayOffset(MethodCall(Variable("$h"), "m", []), "i1"), "i2")]
    #     ),
    # ]
    # eq_ast(input, expected)


def test_assign():
    input = r"""<?php
        $a = 1;
        $b = +2;
        $c = -3;
    ?>"""
    py_ast = translate(input)
    debug(py_ast)
    debug(dump(py_ast))
    output = unparse(py_ast)
    debug(output)
    assert False


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

    check_compiles(input, expected)


def test_object_properties():
    input = r"""<?php
        $object->property;
        $object->foreach;
        $object->$variable;
        $object->$variable->schmariable;
        $object->$variable->$schmariable;
    ?>"""
    expected = ""
    check_compiles(input, expected)
