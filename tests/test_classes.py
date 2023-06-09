from .util import check_compiles


def xxtest_class():
    input = r"""<?php
    class Rocket {
        # protected $fuel;

        # const LAUNCH_PADS = ['p1', 'p2'];

        public function get(int $id) {
            return "TODO";
        }
    }
    """
    expected = ""
    check_compiles(input, expected)


def test_new():
    input = r"""<?php
        new Rocket();
    """
    expected = "Rocket()"
    check_compiles(input, expected)


def test_new_with_args():
    input = r"""<?php
        new Rocket(1);
    """
    expected = "Rocket(1)"
    check_compiles(input, expected)


def test_method_call():
    input = r"""<?php
        $r->fire();
    """
    expected = "r.fire()"
    check_compiles(input, expected)


def test_method_call_with_args():
    input = r"""<?php
        $r->fire(1, 'a');
        $r->fire($arg1=1, $arg2='a');
    """
    expected = "r.fire(1, 'a')\n" "r.fire(\n" "arg1 = 1, \n" "arg2 = 'a')"
    check_compiles(input, expected)
