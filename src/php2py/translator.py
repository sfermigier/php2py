#!/usr/bin/env python

import ast as py

from devtools import debug

from php2py.php_ast import (
    Expr_Assign,
    Expr_Exit,
    Expr_PropertyFetch,
    Expr_StaticCall,
    Node,
    Scalar_LNumber,
    Scalar_String,
    Stmt_Class,
    Stmt_ClassMethod,
    Stmt_Echo,
    Stmt_Expression,
    Stmt_Namespace,
    Stmt_Return,
    Stmt_Use,
)

unary_ops = {
    "~": py.Invert,
    "!": py.Not,
    "+": py.UAdd,
    "-": py.USub,
}

bool_ops = {
    "&&": py.And,
    "||": py.Or,
    "and": py.And,
    "or": py.Or,
}

cmp_ops = {
    "!=": py.NotEq,
    "!==": py.NotEq,
    "<>": py.NotEq,
    "<": py.Lt,
    "<=": py.LtE,
    "==": py.Eq,
    "===": py.Eq,
    ">": py.Gt,
    ">=": py.GtE,
}

binary_ops = {
    "+": py.Add,
    "-": py.Sub,
    "*": py.Mult,
    "/": py.Div,
    "%": py.Mod,
    "<<": py.LShift,
    ">>": py.RShift,
    "|": py.BitOr,
    "&": py.BitAnd,
    "^": py.BitXor,
}

casts = {
    "double": "float",
    "string": "str",
    "array": "list",
}


class Translator:
    def translate_root(self, root_node):
        return py.Module(body=[self.translate(n) for n in root_node], type_ignores=[])

    def translate(self, node):
        debug("Translating node:", node)
        match node:
            case [*_]:
                return [self.translate(n) for n in node]

            case Node():
                node_type = node.__class__.__name__

                if node_type.startswith("Stmt_"):
                    return self.translate_stmt(node)

                if node_type.startswith("Expr_"):
                    return self.translate_expr(node)

                if node_type.startswith("Scalar_"):
                    return self.translate_scalar(node)

                print(f"Ignoring node: {node_type}")

            case _:
                debug(node)
                assert False

    def translate_scalar(self, node):
        match node:
            case Scalar_String(value):
                return py.Str(value)

            case Scalar_LNumber(value):
                return py.Str(value)

    def translate_expr(self, node):
        match node:
            case Expr_Assign():
                # if isinstance(node.node, php.ArrayOffset) and node.node.expr is None:
                #     return py.Call(
                #         py.Attribute(
                #             self.translate(node.node.node),
                #             "append",
                #             py.Load(**pos(node)),
                #             **pos(node),
                #         ),
                #         [self.translate(node.expr)],
                #         [],
                #         None,
                #         None,
                #         **pos(node),
                #     )
                # if isinstance(node.node, php.ObjectProperty) and isinstance(
                #     node.node.name, php.BinaryOp
                # ):
                #     return to_stmt(
                #         py.Call(
                #             py.Name("setattr", py.Load(**pos(node)), **pos(node)),
                #             [
                #                 self.translate(node.node.node),
                #                 self.translate(node.node.name),
                #                 self.translate(node.expr),
                #             ],
                #             [],
                #             None,
                #             None,
                #             **pos(node),
                #         )
                #     )
                # debug(node)
                # debug(node.var)
                # debug(node.expr)
                # assert False
                return py.Assign(
                    [store(self.translate(node.var))],
                    self.translate(node.expr),
                    **pos(node),
                )

            case Expr_StaticCall():
                return

            case Expr_Exit(expr):
                args = []
                if expr is not None:
                    args.append(self.translate(expr))
                return py.Raise(
                    py.Call(
                        py.Name("SystemExit", py.Load()),
                        args,
                        [],
                    ),
                    None,
                )

            case Expr_PropertyFetch(var=var, name=name):
                # if isinstance(node.name, (Variable, BinaryOp)):
                #     return py.Call(
                #         py.Name("getattr", py.Load()),
                #         [self.translate(node.node), self.translate(node.name)],
                #         [],
                #     )
                return py.Attribute(self.translate(var), name, py.Load())

    def translate_stmt(self, node):
        match node:
            case Stmt_Echo():
                return py.Call(
                    py.Name("echo", py.Load()),
                    [self.translate(n) for n in node.exprs],
                    [],
                )

            case Stmt_Expression():
                return self.translate(node.expr)

            case Stmt_Namespace():
                return self.translate(node.stmts)

            case Stmt_Use():
                return self.translate(node.uses)

            # case "Stmt_UseUse":
            #     return translate(node['uses'])

            case Stmt_Class():
                name = node.name.name
                bases = []
                # extends = node.extends or "object"
                # bases.append(py.Name(extends, py.Load(**pos(node)), **pos(node)))

                body = list(map(to_stmt, list(map(self.translate, node.stmts))))

                for stmt in body:
                    if isinstance(stmt, py.FunctionDef) and stmt.name in (
                        name,
                        "__construct",
                    ):
                        stmt.name = "__init__"
                if not body:
                    body = [py.Pass(**pos(node))]
                return py.ClassDef(name, bases, body, [], **pos(node))

            case Stmt_Return(expr):
                if expr is None:
                    return py.Return(None)
                else:
                    return py.Return(self.translate(expr))

            case Stmt_ClassMethod():
                args = []
                defaults = []
                decorator_list = []

                decorator_list.append(
                    py.Name("classmethod", py.Load(**pos(node)), **pos(node))
                )
                args.append(py.Name("cls", py.Param(**pos(node)), **pos(node)))

                # if "static" in node.modifiers:
                #     decorator_list.append(
                #         py.Name("classmethod", py.Load(**pos(node)), **pos(node))
                #     )
                #     args.append(py.Name("cls", py.Param(**pos(node)), **pos(node)))
                # else:
                #     args.append(py.Name("self", py.Param(**pos(node)), **pos(node)))

                # for param in node["args"]:
                #     args.append(py.Name(param.name[1:], py.Param(**pos(node)), **pos(node)))
                #     if param.default is not None:
                #         defaults.append(self.translate(param.default))

                body = list(map(to_stmt, list(map(self.translate, node.stmts))))
                if not body:
                    body = [py.Pass(**pos(node))]

                return py.FunctionDef(
                    node.name,
                    py.arguments(args, None, None, defaults),
                    body,
                    decorator_list,
                    **pos(node),
                )

        # if isinstance(node, php.Assignment):
        #     if isinstance(node.node, php.ArrayOffset) and node.node.expr is None:
        #         return py.Call(
        #             py.Attribute(
        #                 from_phpast(node.node.node),
        #                 "append",
        #                 py.Load(**pos(node)),
        #                 **pos(node),
        #             ),
        #             [from_phpast(node.expr)],
        #             [],
        #             None,
        #             None,
        #             **pos(node),
        #         )
        #     if isinstance(node.node, php.ObjectProperty) and isinstance(
        #         node.node.name, php.BinaryOp
        #     ):
        #         return to_stmt(
        #             py.Call(
        #                 py.Name("setattr", py.Load(**pos(node)), **pos(node)),
        #                 [
        #                     from_phpast(node.node.node),
        #                     from_phpast(node.node.name),
        #                     from_phpast(node.expr),
        #                 ],
        #                 [],
        #                 None,
        #                 None,
        #                 **pos(node),
        #             )
        #         )
        #     return py.Assign(
        #         [store(from_phpast(node.node))], from_phpast(node.expr), **pos(node)
        #     )


def to_stmt(pynode):
    if pynode is None:
        return py.Expr()

    if not isinstance(pynode, py.stmt):
        return py.Expr(pynode, lineno=pynode.lineno, col_offset=pynode.col_offset)

    return pynode


#
# Util
#
def pos(node):
    return {"lineno": 0, "col_offset": 0}
    # return {"lineno": getattr(node, "lineno", 0), "col_offset": 0}


def store(name):
    name.ctx = py.Store(**pos(name))
    return name


def deblock(node):
    if isinstance(node, php.Block):
        return node.nodes
    else:
        return [node]


def build_args(params):
    args = []
    kwargs = []
    for param in params:
        node = from_phpast(param.node)
        if isinstance(node, py.Assign):
            kwargs.append(py.keyword(node.targets[0].id, node.value))
        else:
            args.append(node)
    return args, kwargs


def build_format(left, right):
    if isinstance(left, str):
        pattern, pieces = left.replace("%", "%%"), []
    elif isinstance(left, php.BinaryOp) and left.op == ".":
        pattern, pieces = build_format(left.left, left.right)
    else:
        pattern, pieces = "%s", [left]
    if isinstance(right, str):
        pattern += right.replace("%", "%%")
    else:
        pattern += "%s"
        pieces.append(right)
    return pattern, pieces
