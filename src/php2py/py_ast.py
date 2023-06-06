import ast


def py_parse_stmt(input):
    """Return a Python AST from a python source string."""
    return ast.parse(input).body[0]
