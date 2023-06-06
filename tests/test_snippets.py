from pathlib import Path

import pytest
from devtools import debug

from .util import check_compiles


def get_snippets():
    paths = (Path(__file__).parent / "snippets").glob("*.py")
    for path in paths:
        if path.name.startswith("_"):
            continue
        yield path


@pytest.mark.parametrize("snippet", get_snippets())
def test_snippet(snippet: Path):
    debug(snippet)
    ns = {}
    exec(snippet.read_bytes(), ns)  # noqa: S102
    php = ns["PHP"].strip()
    if "EXPECTED" in ns:
        expected = ns["EXPECTED"].strip()
        check_compiles(php, expected)
    else:
        check_compiles(php)
