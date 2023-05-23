from pathlib import Path
from unittest import skip

from .util import check_compiles


@skip
def test_accounts():
    input = (Path(".") / "programs" / "dummy" / "accounts.php").open().read()
    expected = ""
    check_compiles(input, expected)
