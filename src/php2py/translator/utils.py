import ast as py

from php2py.php_ast import Node


#
# Util
#
def to_stmt(pynode):
    match pynode:
        case None:
            return py.Expr()

        case py.stmt():
            return pynode

        case _:
            return py.Expr(pynode)
            # return py.Expr(pynode, lineno=pynode.lineno, col_offset=pynode.col_offset)


def pos(node: Node) -> dict:
    lineno = getattr(node, "_lineno", 0)
    return {"lineno": lineno, "col_offset": 0}
    # return {"lineno": node._lineno, "col_offset": node._col_offset}


def store(name):
    assert name
    name.ctx = py.Store(**pos(name))
    return name


# def build_format(left, right):
#     if isinstance(left, str):
#         pattern, pieces = left.replace("%", "%%"), []
#     elif isinstance(left, php.BinaryOp) and left.op == ".":
#         pattern, pieces = build_format(left.left, left.right)
#     else:
#         pattern, pieces = "%s", [left]
#     if isinstance(right, str):
#         pattern += right.replace("%", "%%")
#     else:
#         pattern += "%s"
#         pieces.append(right)
#     return pattern, pieces
