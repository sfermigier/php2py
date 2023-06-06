from textwrap import dedent

import pytest

from .util import check_compiles


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
    expected = dedent(
        """\
        a += 5
        b -= 6
        c += d
        e ^= f
    """
    )
    check_compiles(input, expected)


@pytest.mark.skip("TODO")
def test_list_assignment():
    input = r"""<?php
        list($a, $b, $c) = $d;
    ?>"""
    expected = ""
    check_compiles(input, expected)
