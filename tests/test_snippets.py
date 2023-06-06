from pathlib import Path

from devtools import debug
from pytest import mark

from .util import check_compiles


def get_snippets():
    return (Path(__file__).parent / "snippets").glob("*.py")


@mark.parametrize("snippet", get_snippets())
def test_snippet(snippet: Path):
    debug(snippet)
    ns = {}
    exec(snippet.read_bytes(), ns)
    php = ns["PHP"].strip()
    if "EXPECTED" in ns:
        expected = ns["EXPECTED"].strip()
        check_compiles(php, expected)
    else:
        check_compiles(php)
