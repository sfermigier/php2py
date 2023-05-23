# php2py

[![image](https://img.shields.io/pypi/v/php2py.svg)](https://pypi.python.org/pypi/php2py)

[![image](https://img.shields.io/travis/sfermigier/php2py.svg)](https://travis-ci.com/sfermigier/php2py)

[![Documentation Status](https://readthedocs.org/projects/php2py/badge/?version=latest)](https://php2py.readthedocs.io/en/latest/?version=latest)

PHP to Python transpiler.

-   Free software: GNU General Public License v3
-   Documentation: <https://php2py.readthedocs.io> (nope!).

## Use cases

- Helping port PHP code to Python (provides a first pass, which can then be
  manually edited).

## Features

- Translates a subset of PHP to Python. 

## Install

- You need PHP and composer installed on your system.
- You need Python 3.10+.

### For development

- From a git checkout, run

```bash
poetry shell
poetry install
composer install
```

### For actual use

This should work:

```bash
pipx install php2py
```

## Architecture

- Front-end (PHP parser): uses an external PHP parser (nikic/php-parser) to
  parse PHP code and build an AST.
- Back-end (Python generator): uses the AST to generate Python code, via pattern matching.
- Python code is generated from AST using the `unparse` from the stdlib.

## TODO

- Add test cases (real programs) and make sure they pass.
- Make a runtime / stdlib of common PHP functions in Python.
- Cleanup.

## Contributing

I don't have time to work on this project ATM, but I'm happy to review pull requests.

If you are a student (or a group of students) in a computer science or engineering program, and you want to work on this, please contact me (<mailto:sf@abilian.com>).

## Credits

This package was created with [Cruft](https://cruft.github.io/cruft/) and the
[abilian/cookiecutter-abilian-python](https://github.com/abilian/cookiecutter-abilian-python)
project template.

This project uses the `nikic/php-parser` PHP parser (in PHP).
