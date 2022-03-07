from util import check_compiles


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
