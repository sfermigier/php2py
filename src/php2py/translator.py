#!/usr/bin/env python

import ast as py

import rich
from devtools import debug

from php2py.php_ast import (
    Const,
    Expr_Array,
    Expr_ArrayItem,
    Expr_Assign,
    Expr_AssignOp_BitwiseXor,
    Expr_AssignOp_Concat,
    Expr_AssignOp_Minus,
    Expr_AssignOp_Plus,
    Expr_BinaryOp_Div,
    Expr_BinaryOp_Minus,
    Expr_BinaryOp_Mul,
    Expr_BinaryOp_Plus,
    Expr_BitwiseNot,
    Expr_BooleanNot,
    Expr_ConstFetch,
    Expr_Exit,
    Expr_FuncCall,
    Expr_Isset,
    Expr_MethodCall,
    Expr_New,
    Expr_PropertyFetch,
    Expr_StaticCall,
    Expr_UnaryMinus,
    Expr_UnaryPlus,
    Expr_Variable,
    Identifier,
    Name,
    Node,
    Scalar_DNumber,
    Scalar_LNumber,
    Scalar_String,
    Stmt_Break,
    Stmt_Class,
    Stmt_ClassConst,
    Stmt_ClassMethod,
    Stmt_Continue,
    Stmt_Echo,
    Stmt_Expression,
    Stmt_For,
    Stmt_Foreach,
    Stmt_Function,
    Stmt_If,
    Stmt_Namespace,
    Stmt_Nop,
    Stmt_Property,
    Stmt_Return,
    Stmt_Throw,
    Stmt_Use,
    Stmt_While,
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
        # debug("Translating node:", node)
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

                else:
                    return self.translate_other(node)

            case _:
                debug(node)
                assert False

    def translate_other(self, node):
        match node:
            case Name():
                debug(node)

            case _:
                rich.print(f"[red]Ignoring node: {node}[/red]")

    def translate_scalar(self, node):
        match node:
            case Scalar_String(value):
                return py.Str(value)

            case Scalar_LNumber(value):
                return py.Num(value)

            case Scalar_DNumber(value):
                return py.Num(value)

            case _:
                debug(node)
                raise NotImplementedError()

    def translate_expr(self, node):
        match node:
            case Expr_Variable(name):
                if name == "this":
                    name = "self"
                return py.Name(name, py.Load())

            case Expr_ConstFetch():
                # FIXME: 'parts' should be directly addressable
                parts = node.name._json["parts"]
                name = parts[0]
                if name.lower() == "true":
                    name = "True"
                elif name.lower() == "false":
                    name = "False"
                elif name.lower() == "null":
                    name = "None"
                else:
                    raise NotImplemented(str(name))

                return py.Name(name, py.Load())

            case Expr_Array(items=items):
                if not items:
                    return py.List([], py.Load(**pos(node)), **pos(node))

                elif items[0].key is None:
                    return py.List(
                        [self.translate(x.value) for x in items],
                        py.Load(**pos(node)),
                        **pos(node),
                    )

                else:
                    keys = []
                    values = []
                    for elem in items:
                        keys.append(self.translate(elem.key))
                        values.append(self.translate(elem.value))
                    return py.Dict(keys, values, **pos(node))

            #
            # Unary & binary ops
            #
            case Expr_UnaryPlus(expr):
                return py.UnaryOp(py.UAdd(), self.translate(expr))

            case Expr_UnaryMinus(expr):
                return py.UnaryOp(py.USub(), self.translate(expr))

            case Expr_BinaryOp_Plus(left=left, right=right):
                return py.BinOp(self.translate(left), py.Add(), self.translate(right))

            case Expr_BinaryOp_Minus(left=left, right=right):
                return py.BinOp(self.translate(left), py.Sub(), self.translate(right))

            case Expr_BinaryOp_Mul(left=left, right=right):
                return py.BinOp(self.translate(left), py.Mult(), self.translate(right))

            case Expr_BinaryOp_Div(left=left, right=right):
                return py.BinOp(self.translate(left), py.Div(), self.translate(right))

            case Expr_BooleanNot(expr):
                return py.UnaryOp(py.Not(), self.translate(expr))

            case Expr_BitwiseNot(expr):
                return py.UnaryOp(py.Invert(), self.translate(expr))

            #
            # Assign ops
            #
            case Expr_AssignOp_Plus(var=var, expr=expr):
                return py.AugAssign(
                    target=py.Name(id="xxx", ctx=py.Store()),
                    op=py.Add(),
                    value=self.translate(expr),
                )
                # debug(node)
                # assert False
                # return from_phpast(
                #     php.Assignment(
                #         node.left,
                #         php.BinaryOp(node.op[:-1], node.left, node.right, lineno=node.lineno),
                #         False,
                #         lineno=node.lineno,
                #     )
                # )

            case Expr_AssignOp_Minus(var=var, expr=expr):
                return py.AugAssign(
                    target=py.Name(id="xxx", ctx=py.Store()),
                    op=py.Sub(),
                    value=self.translate(expr),
                )

            case Expr_AssignOp_Concat(var=var, expr=expr):
                return py.AugAssign(
                    target=py.Name(id="xxx", ctx=py.Store()),
                    op=py.Add(),
                    value=self.translate(expr),
                )
                pass

            case Expr_AssignOp_BitwiseXor(var=var, expr=expr):
                return py.AugAssign(
                    target=py.Name(id="xxx", ctx=py.Store()),
                    op=py.BitXor(),
                    value=self.translate(expr),
                )

            case Expr_Assign(var=var, expr=expr):
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

                return py.Assign(
                    [store(self.translate(var))],
                    self.translate(expr),
                    **pos(node),
                )

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

            case Expr_Isset(vars):
                # if isinstance(node, php.IsSet) and len(node.nodes) == 1:
                if isinstance(node.nodes[0], php.ArrayOffset):
                    return py.Compare(
                        self.translate(node.nodes[0].expr),
                        [py.In(**pos(node))],
                        [self.translate(node.nodes[0].node)],
                        **pos(node),
                    )
                if isinstance(node.nodes[0], php.ObjectProperty):
                    return py.Call(
                        py.Name("hasattr", py.Load(**pos(node)), **pos(node)),
                        [
                            self.translate(node.nodes[0].node),
                            self.translate(node.nodes[0].name),
                        ],
                        [],
                        None,
                        None,
                        **pos(node),
                    )
                if isinstance(node.nodes[0], php.Variable):
                    return py.Compare(
                        py.Str(node.nodes[0].name[1:], **pos(node)),
                        [py.In(**pos(node))],
                        [
                            py.Call(
                                py.Name("vars", py.Load(**pos(node)), **pos(node)),
                                [],
                                [],
                                None,
                                None,
                                **pos(node),
                            )
                        ],
                        **pos(node),
                    )
                return py.Compare(
                    self.translate(vars[0]), [py.IsNot()], [py.Name("None", py.Load())]
                )

            case Expr_FuncCall(name=name, args=args):
                name = name._json["parts"][0]
                func = py.Name(name, py.Load())

                # if isinstance(name, str):
                #     name = py.Name(name, py.Load())
                # else:
                #     name = py.Subscript(
                #         py.Call(
                #             func=py.Name("vars", py.Load()),
                #             args=[],
                #             keywords=[],
                #             **pos(node),
                #         ),
                #         py.Index(self.translate(node.name)),
                #         py.Load(),
                #     )
                # args, kwargs = build_args(node.params)
                return py.Call(func=func, args=args, keywords=[], **pos(node))

            case Expr_New(class_=class_, args=args):
                name = class_._json["parts"][0]
                func = py.Name(name, py.Load())
                return py.Call(func=func, args=args, keywords=[], **pos(node))

            case Expr_MethodCall(var=var, name=name, args=args):
                name = name.name
                func = py.Attribute(self.translate(var), name, py.Load())
                return py.Call(func=func, args=args, keywords=[], **pos(node))

            case Expr_StaticCall():
                return

            case _:
                debug(node)
                raise NotImplementedError(
                    f"Don't know how to translate node {node.__class__}"
                )

    def translate_stmt(self, node):
        match node:
            case Stmt_Nop():
                return py.Pass()

            case Stmt_Echo():
                return py.Call(
                    py.Name("echo", py.Load()),
                    [self.translate(n) for n in node.exprs],
                    [],
                )

            case Stmt_Expression(expr):
                return py.Expr(value=self.translate(expr))

            case Stmt_Namespace(stmts=stmts):
                return self.translate(stmts)

            case Stmt_Use(uses=uses):
                return self.translate(uses)

            #
            # Control flow
            #
            case Stmt_If(cond=cond, stmts=stmts, else_=else_):
                if else_:
                    orelse = [
                        to_stmt(self.translate(stmt)) for stmt in node.else_.stmts
                    ]
                else:
                    orelse = []

                for elseif in reversed(node.elseifs):
                    orelse = [
                        py.If(
                            self.translate(elseif.expr),
                            [to_stmt(self.translate(stmt)) for stmt in stmts],
                            orelse,
                            **pos(node),
                        )
                    ]

                return py.If(
                    self.translate(cond),
                    [to_stmt(self.translate(stmt)) for stmt in stmts],
                    orelse,
                    **pos(node),
                )

            case Stmt_For():
                assert (
                    node.test is None or len(node.test) == 1
                ), "only a single test is supported in for-loops"

                return from_phpast(
                    php.Block(
                        (node.start or [])
                        + [
                            php.While(
                                node.test[0] if node.test else 1,
                                php.Block(
                                    deblock(node.node) + (node.count or []),
                                    lineno=node.lineno,
                                ),
                                lineno=node.lineno,
                            )
                        ],
                        lineno=node.lineno,
                    )
                )

            case Stmt_Foreach(expr=expr, valueVar=value_var, stmts=stmts):
                debug(value_var)
                if node.keyVar is None:
                    target = py.Name(value_var.name, py.Store(**pos(node)), **pos(node))
                else:
                    target = py.Tuple(
                        [
                            py.Name(node.keyVar.name[1:], py.Store(**pos(node))),
                            py.Name(node.valueVar.name[1:], py.Store(**pos(node))),
                        ],
                        py.Store(**pos(node)),
                        **pos(node),
                    )

                return py.For(
                    target,
                    self.translate(expr),
                    [to_stmt(self.translate(stmt)) for stmt in stmts],
                    [],
                    **pos(node),
                )

            case Stmt_While(cond=cond, stmts=stmts):
                return py.While(
                    self.translate(cond),
                    [to_stmt(self.translate(stmt)) for stmt in stmts],
                    [],
                    **pos(node),
                )

            case Stmt_Break(num=num):
                assert num is None, "level on break not supported"
                return py.Break(**pos(node))

            case Stmt_Continue(num=num):
                assert num is None, "level on continue not supported"
                return py.Continue(**pos(node))

            # case Stmt_DoWhile():
            #     condition = php.If(
            #         php.UnaryOp("!", node.expr, lineno=node.lineno),
            #         php.Break(None, lineno=node.lineno),
            #         [],
            #         None,
            #         lineno=node.lineno,
            #     )
            #     return from_phpast(
            #         php.While(
            #             1,
            #             php.Block(deblock(node.node) + [condition], lineno=node.lineno),
            #             lineno=node.lineno,
            #         )
            #     )

            #
            # Functions / methods
            #
            case Stmt_Function(name=name, params=params, stmts=stmts):
                args = []
                defaults = []
                for param in params:
                    param_name = param.var.name
                    args.append(py.Name(param_name, py.Param()))
                    if param.default is not None:
                        defaults.append(self.translate(param.default))

                body = [to_stmt(self.translate(stmt)) for stmt in stmts]
                if not body:
                    body = [py.Pass(**pos(node))]

                arguments = py.arguments(
                    posonlyargs=[],
                    args=args,
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=defaults,
                )
                return py.FunctionDef(name.name, arguments, body, [], **pos(node))

            # case Stmt_StaticMethodCall():
            #     class_ = node.class_
            #     if class_ == "self":
            #         class_ = "cls"
            #     args, kwargs = build_args(node.params)
            #     return py.Call(
            #         py.Attribute(
            #             py.Name(class_, py.Load(**pos(node)), **pos(node)),
            #             node.name,
            #             py.Load(**pos(node)),
            #             **pos(node),
            #         ),
            #         args,
            #         kwargs,
            #         None,
            #         None,
            #         **pos(node),
            #     )

            case Stmt_Return(expr):
                if expr is None:
                    return py.Return(None)
                else:
                    return py.Return(self.translate(expr))

            #
            # Class definitions
            #
            case Stmt_Class(name=name, stmts=stmts):
                name = name.name
                bases = []
                # extends = node.extends or "object"
                # bases.append(py.Name(extends, py.Load(**pos(node)), **pos(node)))

                body = [to_stmt(self.translate(stmt)) for stmt in stmts]
                for stmt in body:
                    if isinstance(stmt, py.FunctionDef) and stmt.name in (
                        name,
                        "__construct",
                    ):
                        stmt.name = "__init__"
                if not body:
                    body = [py.Pass(**pos(node))]

                return py.ClassDef(name, bases, body, [], **pos(node))

            case Stmt_ClassMethod(stmts=stmts):
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

                body = [to_stmt(self.translate(stmt)) for stmt in stmts]
                if not body:
                    body = [py.Pass(**pos(node))]

                return py.FunctionDef(
                    node.name,
                    py.arguments(args, None, None, defaults),
                    body,
                    decorator_list,
                    **pos(node),
                )

            # case Stmt_Method():
            #     args = []
            #     defaults = []
            #     decorator_list = []
            #     if "static" in node.modifiers:
            #         decorator_list.append(
            #             py.Name("classmethod", py.Load(**pos(node)), **pos(node))
            #         )
            #         args.append(py.Name("cls", py.Param(**pos(node)), **pos(node)))
            #     else:
            #         args.append(py.Name("self", py.Param(**pos(node)), **pos(node)))
            #     for param in node.params:
            #         args.append(py.Name(param.name[1:], py.Param(**pos(node)), **pos(node)))
            #         if param.default is not None:
            #             defaults.append(from_phpast(param.default))
            #     body = list(map(to_stmt, list(map(from_phpast, node.nodes))))
            #     if not body:
            #         body = [py.Pass(**pos(node))]
            #     return py.FunctionDef(
            #         node.name,
            #         py.arguments(args, None, None, defaults),
            #         body,
            #         decorator_list,
            #         **pos(node),
            #     )

            # if isinstance(node, php.Assignment):
            #     if isinstance(node.node, php.ArrayOffset) and node.node.expr is None:
            #         return py.Call(
            #             py.Attribute(
            #                 self.translate(node.node.node),
            #                 "append",
            #                 py.Load(**pos(node)),
            #                 **pos(node),
            #             ),
            #             [self.translate(node.expr)],
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
            #                     self.translate(node.node.node),
            #                     self.translate(node.node.name),
            #                     self.translate(node.expr),
            #                 ],
            #                 [],
            #                 None,
            #                 None,
            #                 **pos(node),
            #             )
            #         )
            #     return py.Assign(
            #         [store(self.translate(node.node))], self.translate(node.expr), **pos(node)
            #     )

            #     if isinstance(node, (php.ClassConstants, php.ClassVariables)):
            case Stmt_ClassConst(consts=consts):
                _ignore = Stmt_ClassConst(
                    flags=0,
                    attrGroups=[],
                    consts=[
                        Const(
                            namespacedName=None,
                            name=Identifier(name="LAUNCH_PADS"),
                            value=Expr_Array(
                                items=[
                                    Expr_ArrayItem(
                                        byRef=False,
                                        unpack=False,
                                        key=None,
                                        value=Scalar_String(value="p1"),
                                    ),
                                    Expr_ArrayItem(
                                        byRef=False,
                                        unpack=False,
                                        key=None,
                                        value=Scalar_String(value="p2"),
                                    ),
                                ]
                            ),
                        )
                    ],
                )

                body = []
                for const in consts:
                    pass

                msg = "only one class-level assignment supported per line"
                assert len(node.nodes) == 1, msg

                if isinstance(node.nodes[0], php.ClassConstant):
                    name = php.Constant(node.nodes[0].name, lineno=node.lineno)
                else:
                    name = php.Variable(node.nodes[0].name, lineno=node.lineno)
                initial = node.nodes[0].initial
                if initial is None:
                    initial = php.Constant("None", lineno=node.lineno)

                return py.Assign(
                    [store(self.translate(name))], self.translate(initial), **pos(node)
                )

            case Stmt_Property():
                if isinstance(node.name, (php.Variable, php.BinaryOp)):
                    return py.Call(
                        py.Name("getattr", py.Load(**pos(node)), **pos(node)),
                        [from_phpast(node.node), from_phpast(node.name)],
                        [],
                        None,
                        None,
                        **pos(node),
                    )
                return py.Attribute(
                    self.translate(node.node),
                    node.name,
                    py.Load(**pos(node)),
                    **pos(node),
                )

            #
            # Exceptions
            #
            # if isinstance(node, php.Try):
            #     return py.TryExcept(
            #         list(map(to_stmt, list(map(from_phpast, node.nodes)))),
            #         [
            #             py.ExceptHandler(
            #                 py.Name(catch.class_, py.Load(**pos(node)), **pos(node)),
            #                 store(from_phpast(catch.var)),
            #                 list(map(to_stmt, list(map(from_phpast, catch.nodes)))),
            #                 **pos(node),
            #             )
            #             for catch in node.catches
            #         ],
            #         [],
            #         **pos(node),
            #     )

            case Stmt_Throw(expr):
                return py.Raise(self.translate(expr), None, None, **pos(node))

            case _:
                debug(node)
                raise NotImplementedError(
                    f"Don't know how to translate node {node.__class__}"
                )


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
    return {"lineno": 0, "col_offset": 0}
    # return {"lineno": node._lineno, "col_offset": node._col_offset}


def store(name):
    name.ctx = py.Store(**pos(name))
    return name


def deblock(node):
    if isinstance(node, Block):
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
