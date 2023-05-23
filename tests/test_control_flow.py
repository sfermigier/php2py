from unittest import skip

from .util import check_compiles


def test_while():
    input = r"""<?php
        while (true) {
            echo $bar;
        }
    ?>"""
    expected = "while True:\n" "    echo(bar)"
    check_compiles(input, expected)


def test_while_with_break_and_continue():
    input = r"""<?php
        while (true) {
            echo $bar;
            break;
        }
        while (true) {
            echo $bar;
            continue;
        }
    ?>"""
    expected = (
        "while True:\n"
        "    echo(bar)\n"
        "    break\n"
        "while True:\n"
        "    echo(bar)\n"
        "    continue"
    )
    check_compiles(input, expected)


def test_if():
    input = r"""<?php
        if (true) {
            echo $bar;
        }

        if (true) {
            echo $bar;
        } else {
            echo "bah";
        }

        if (true) {
            echo $bar;
        } else if (false) {
            echo "bah";
        }

    ?>"""
    expected = (
        "if True:\n"
        "    echo(bar)\n"
        "if True:\n"
        "    echo(bar)\n"
        "else:\n"
        "    echo('bah')\n"
        "if True:\n"
        "    echo(bar)\n"
        "elif False:\n"
        "    echo('bah')"
    )
    check_compiles(input, expected)


def test_foreach():
    input = r"""<?php
        foreach ($foo as $bar) {
            echo $bar;
        }
        # TODO
        # foreach ($spam as $ham => $eggs) {
        #     echo "$ham: $eggs";
        # }
        # foreach (complex($expression) as &$ref)
        #     $ref++;
        # foreach ($what as $de => &$dealy):
        #     yo();
        #     yo();
        # endforeach;
        # foreach ($foo as $bar[0]) {}
    ?>"""
    expected = "for bar in foo:\n" "    echo(bar)\n" "pass"
    check_compiles(input, expected)


@skip("TODO")
def test_for():
    input = r"""<?php
        for ($i = 0; $i < 10; $i++) {
            echo $i;
        }
    ?>"""
    expected = ""
    check_compiles(input, expected)
