from pathlib import Path

from util import check_compiles


def test_accounts():
    input = (Path(".") / "programs" / "dummy" / "accounts.php").open().read()
    expected = ""
    check_compiles(input, expected)