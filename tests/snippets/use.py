PHP = r"""
<?php
use PHPCR\PropertyType;
use PHPCR\Util\ValueConverter;
"""

EXPECTED = r"""
from PHPCR.PropertyType import *
from PHPCR.Util.ValueConverter import *
"""
