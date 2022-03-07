from util import check_compiles

from php2py.parser import parse
from php2py.php_ast import Stmt_InlineHTML, Stmt_Nop


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
    expected = "a = 1\n" "\n" "b = +2\n" "\n" "c = -3"
    check_compiles(input, expected)


def test_assign2():
    input = r"""<?php
        $c = !$d;
        $e = ~$f;
    ?>"""
    expected = "c = not d\n" "\n" "e = ~f"
    check_compiles(input, expected)


def test_assignment_ops():
    input = r"""<?php
        $a += 5;
        $b -= 6;
        $c .= $d;
        $e ^= $f;
    ?>"""
    expected = "xxx += 5\n" "\n" "xxx -= 6\n" "\n" "xxx += d\n" "\n" "xxx ^= f"
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


def test_object_properties():
    input = r"""<?php
        $object->property;
        $object->foreach;
        $object->$variable;
        $object->$variable->schmariable;
        $object->$variable->$schmariable;
    ?>"""
    expected = (
        "object.property\n"
        "object.foreach\n"
        "object.variable\n"
        "object.variable.schmariable\n"
        "object.variable.schmariable"
    )
    check_compiles(input, expected)


def test_array():
    input = r"""<?php
        $l = [1, 2, 3];
        $l = ['a', 1.2, [null, true, false]];
        $d = [1 => 2, 'a' => 'b'];
    """
    expected = (
        "l = [1, 2, 3]\n"
        "\n"
        "l = ['a', 1.2, [None, True, False]]\n"
        "\n"
        "d = {1: 2, 'a': 'b'}"
    )
    check_compiles(input, expected)


def test_unset_isset():
    input = r"""<?php
        $x = 1;
        isset($x);
        unset($x);
    """
    expected = "x = 1\n" "'x' in vars()\n" "del x"
    check_compiles(input, expected)
