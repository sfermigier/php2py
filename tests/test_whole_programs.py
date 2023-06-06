from pathlib import Path

from devtools import debug
from pytest import mark

from .util import check_compiles


def get_programs():
    return (Path(__file__).parent / "programs").glob("*.php")


@mark.parametrize("program", get_programs())
def test_program(program: Path):
    debug(program)
    php = program.read_text()
    check_compiles(php)
