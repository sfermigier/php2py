from pathlib import Path

import pytest
from devtools import debug

from .util import check_compiles


def get_programs():
    paths = (Path(__file__).parent / "programs").glob("*.php")
    for path in paths:
        if path.name.startswith("_"):
            continue
        yield path


@pytest.mark.parametrize("program", get_programs())
def test_program(program: Path):
    debug(program)
    php = program.read_text()
    check_compiles(php)
