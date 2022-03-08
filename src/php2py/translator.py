#!/usr/bin/env python

import ast as py

import rich
from devtools import debug

from php2py.php_ast import (
    Arg,
    Expr_Array,
    Expr_ArrayDimFetch,
    Expr_Assign,
    Expr_AssignOp_BitwiseXor,
    Expr_AssignOp_Concat,
    Expr_AssignOp_Minus,
    Expr_AssignOp_Plus,
    Expr_BinaryOp,
    Expr_BinaryOp_BooleanAnd,
    Expr_BooleanNot,
    Expr_Cast,
    Expr_Cast_Array,
    Expr_Cast_Bool,
    Expr_Cast_Double,
    Expr_Cast_Int,
    Expr_Cast_Object,
    Expr_Cast_String,
    Expr_ClassConstFetch,
    Expr_Closure,
    Expr_ConstFetch,
    Expr_Empty,
    Expr_Exit,
    Expr_FuncCall,
    Expr_Isset,
    Expr_MethodCall,
    Expr_New,
    Expr_PostDec,
    Expr_PostInc,
    Expr_PreDec,
    Expr_PreInc,
    Expr_PropertyFetch,
    Expr_StaticCall,
    Expr_Ternary,
    Expr_UnaryOp,
    Expr_Variable,
    Name,
    Node,
    Scalar_DNumber,
    Scalar_LNumber,
    Scalar_String,
    Stmt_Break,
    Stmt_Class,
    Stmt_ClassMethod,
    Stmt_Continue,
    Stmt_Echo,
    Stmt_Expression,
    Stmt_For,
    Stmt_Foreach,
    Stmt_Function,
    Stmt_If,
    Stmt_InlineHTML,
    Stmt_Namespace,
    Stmt_Nop,
    Stmt_Property,
    Stmt_Return,
    Stmt_Throw,
    Stmt_TryCatch,
    Stmt_Unset,
    Stmt_Use,
    Stmt_While,
)

unary_ops = {
    "~": py.Invert,
    "!": py.Not,
    "+": py.UAdd,
    "-": py.USub,
}

binary_ops = {
    # Numbers
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
    # Strings
    ".": py.Add,
}

bool_ops = {
    "&&": py.And,
    "||": py.Or,
    "and": py.And,
    "or": py.Or,
}

compare_ops = {
    "!=": py.NotEq,
    "!==": py.IsNot,
    "<>": py.NotEq,
    "<": py.Lt,
    "<=": py.LtE,
    "==": py.Eq,
    "===": py.Is,
    ">": py.Gt,
    ">=": py.GtE,
}

# casts = {
#     "double": "float",
#     "string": "str",
#     "array": "list",
# }


class Translator:
    def translate_root(self, root_node):
        return py.Module(body=[self.translate(n) for n in root_node], type_ignores=[])

    def translate(self, node):
        # debug(node)
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
            case Arg(name=name, value=value):
                debug(node)
                assert False, "Should not happen"

            case Name():
                debug(node)
                assert False, "Should not happen"

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
                    raise NotImplementedError(str(name))

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
            # Unary ops
            #
            case Expr_UnaryOp(expr):
                op = unary_ops[node.op]()
                return py.UnaryOp(op, self.translate(expr))

            #
            # Binary ops
            #
            case Expr_BinaryOp(left, right):
                if node.op in binary_ops:
                    op = binary_ops[node.op]()
                    return py.BinOp(self.translate(left), op, self.translate(right))

                elif node.op in compare_ops:
                    op = compare_ops[node.op]()
                    return py.Compare(
                        self.translate(left),
                        [op],
                        [self.translate(node.right)],
                        **pos(node),
                    )

                elif node.op in bool_ops:
                    op = bool_ops[node.op]()
                    return py.BoolOp(
                        op, [self.translate(left), self.translate(right)], **pos(node)
                    )

                else:
                    debug(node)
                    raise NotImplementedError(node.__class__.__name__)

            # TODO: check this:
            #         if node.op == ".":
            #             pattern, pieces = build_format(node.left, node.right)
            #             if pieces:
            #                 return py.BinOp(
            #                     py.Str(pattern, **pos(node)),
            #                     py.Mod(**pos(node)),
            #                     py.Tuple(
            #                         list(map(from_phpast, pieces)),
            #                         py.Load(**pos(node)),
            #                         **pos(node),
            #                     ),
            #                     **pos(node),
            #                 )
            #             else:
            #                 return py.Str(pattern % (), **pos(node))
            #         op = binary_ops.get(node.op)
            #         if node.op == "instanceof":
            #             return py.Call(
            #                 func=py.Name(id="isinstance", ctx=py.Load(**pos(node))),
            #                 args=[from_phpast(node.left), from_phpast(node.right)],
            #                 keywords=[],
            #                 starargs=None,
            #                 kwargs=None,
            #             )
            #         assert op is not None, f"unknown binary operator: '{node.op}'"
            #         op = op(**pos(node))
            #         return py.BinOp(
            #             from_phpast(node.left), op, from_phpast(node.right), **pos(node)
            #         )

            # other ops
            case Expr_Ternary(cond=cond, if_=if_, else_=else_):
                return py.IfExp(
                    self.translate(cond),
                    self.translate(if_),
                    self.translate(else_),
                    **pos(node),
                )

            case Expr_PostInc() | Expr_PreDec() | Expr_PreInc() | Expr_PostDec():
                return py.Str(f"TODO: {node.__class__.__name__}")

            # Casts
            case Expr_Cast(expr):
                # TODO: proper cast

                cast_name = {
                    Expr_Cast_Object: "TODO: cast object",
                    Expr_Cast_Array: "TODO: cast array",
                    Expr_Cast_Bool: "bool",
                    Expr_Cast_Double: "float",
                    Expr_Cast_Int: "int",
                    Expr_Cast_String: "str",
                }.get(node.__class__)

                return py.Call(
                    func=py.Name(cast_name, py.Load()),
                    args=[self.translate(expr)],
                    keywords=[],
                    **pos(node),
                )

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
                        func=py.Name("SystemExit", py.Load()),
                        args=args,
                        keywords=[],
                    ),
                    None,
                    **pos(node),
                )

            case Expr_PropertyFetch(var=var, name=name):
                name = name.name
                # if isinstance(node.name, (Variable, BinaryOp)):
                #     return py.Call(
                #         py.Name("getattr", py.Load()),
                #         [self.translate(node.node), self.translate(node.name)],
                #         [],
                #     )
                result = py.Attribute(
                    value=self.translate(var), attr=name, ctx=py.Load(), **pos(node)
                )
                assert isinstance(result.attr, str)
                return result

            case Expr_Isset(vars):
                assert len(vars) == 1
                var = vars[0]
                match var:
                    # case Expr_ArrayOffset():
                    #     return py.Compare(
                    #         self.translate(node.nodes[0].expr),
                    #         [py.In(**pos(node))],
                    #         [self.translate(node.nodes[0].node)],
                    #         **pos(node),
                    #     )
                    #
                    # case Expr_ObjectProperty():
                    #     return py.Call(
                    #         func=py.Name("hasattr", py.Load()),
                    #         args=[
                    #             self.translate(node.nodes[0].node),
                    #             self.translate(node.nodes[0].name),
                    #         ],
                    #         keywords=[],
                    #         **pos(node),
                    #     )

                    case Expr_Variable():
                        return py.Compare(
                            py.Str(var.name),
                            [py.In()],
                            [
                                py.Call(
                                    func=py.Name("vars", py.Load()),
                                    args=[],
                                    keywords=[],
                                )
                            ],
                            **pos(node),
                        )

                    case _:
                        return py.Compare(
                            self.translate(var),
                            [py.IsNot()],
                            [py.Name("None", py.Load())],
                        )

            case Expr_Empty(expr):
                return self.translate(
                    Expr_BooleanNot(
                        Expr_BinaryOp_BooleanAnd(Expr_Isset([node.expr]), expr)
                    )
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
                args, kwargs = self.build_args(args)
                return py.Call(func=func, args=args, keywords=kwargs, **pos(node))

            case Expr_New(class_=class_, args=args):
                args, kwargs = self.build_args(args)
                name = class_._json["parts"][0]
                func = py.Name(name, py.Load())
                return py.Call(func=func, args=args, keywords=kwargs, **pos(node))

            case Expr_MethodCall(var=var, name=name, args=args):
                name = name.name
                args, kwargs = self.build_args(args)
                func = py.Attribute(value=self.translate(var), attr=name, ctx=py.Load())
                return py.Call(func=func, args=args, keywords=kwargs, **pos(node))

            case Expr_StaticCall(class_, name, args):
                class_name = class_._json["parts"][0]
                if class_name == "self":
                    class_name = "cls"
                args, kwargs = self.build_args(args)
                func = py.Attribute(
                    value=py.Name(class_name, py.Load()), attr=name.name, ctx=py.Load()
                )
                assert isinstance(func.attr, str)

                return py.Call(func=func, args=args, keywords=kwargs, **pos(node))

            case Expr_ArrayDimFetch(var=var, dim=dim):
                if dim:
                    return py.Subscript(
                        value=self.translate(var),
                        slice=py.Index(self.translate(dim)),
                        ctx=py.Load(),
                        **pos(node),
                    )
                else:
                    # TODO
                    return py.Str("TODO: ")
                    # return py.Subscript(
                    #     value=self.translate(var),
                    #     slice=py.Index(self.translate(dim)),
                    #     ctx=py.Load(),
                    #     **pos(node),
                    # )

            case Expr_ClassConstFetch(name=name, class_=class_):
                class_name = class_._json["parts"][0]
                return py.Attribute(
                    value=py.Name(id=class_name, ctx=py.Load()),
                    attr=name.name,
                    ctx=py.Load(),
                    **pos(node),
                )

            case Expr_Closure():
                debug(node, node._json)
                raise NotImplementedError(node.__class__.__name__)

            case _:
                debug(node)
                raise NotImplementedError(
                    f"Don't know how to translate node {node.__class__}"
                )

    def translate_stmt(self, node):
        match node:
            case Stmt_Nop():
                return py.Pass(**pos(node))

            case Stmt_Echo(exprs):
                return py.Call(
                    func=py.Name("echo", py.Load()),
                    args=[self.translate(n) for n in exprs],
                    keywords=[],
                    **pos(node),
                )

            case Stmt_Expression(expr):
                return py.Expr(value=self.translate(expr), **pos(node))

            case Stmt_Namespace(stmts=stmts):
                return self.translate(stmts)

            case Stmt_Use(uses=uses):
                return self.translate(uses)

            case Stmt_InlineHTML(value):
                args = [py.Str(value)]
                return py.Call(
                    func=py.Name("inline_html", py.Load()),
                    args=args,
                    keywords=[],
                    **pos(node),
                )

            case Stmt_Unset(vars):
                return py.Delete([self.translate(n) for n in vars], **pos(node))

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
                            test=self.translate(elseif.expr),
                            body=[to_stmt(self.translate(stmt)) for stmt in stmts],
                            orelse=orelse,
                        )
                    ]

                return py.If(
                    test=self.translate(cond),
                    body=[to_stmt(self.translate(stmt)) for stmt in stmts],
                    orelse=orelse,
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
                if node.keyVar is None:
                    target = py.Name(value_var.name, py.Store())
                else:
                    target = py.Tuple(
                        [
                            py.Name(node.keyVar.name[1:], py.Store()),
                            py.Name(node.valueVar.name[1:], py.Store()),
                        ],
                        py.Store(),
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
                    body = [py.Pass()]

                return py.ClassDef(
                    name=name,
                    bases=bases,
                    keywords=[],
                    body=body,
                    decorator_list=[],
                    **pos(node),
                )

            case Stmt_ClassMethod(name=name, params=params, stmts=stmts):
                args = []
                defaults = []
                decorator_list = []

                decorator_list.append(py.Name("classmethod", py.Load()))
                args.append(py.Name("cls", py.Param()))

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
                    body = [py.Pass()]

                arguments = py.arguments(
                    posonlyargs=[],
                    args=args,
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=defaults,
                )

                return py.FunctionDef(
                    name.name, arguments, body, decorator_list, **pos(node)
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
            # case Stmt_ClassConst(consts=consts):
            #     body = []
            #     for const in consts:
            #         pass
            #
            #     msg = "only one class-level assignment supported per line"
            #     assert len(node.nodes) == 1, msg
            #
            #     if isinstance(node.nodes[0], php.ClassConstant):
            #         name = php.Constant(node.nodes[0].name, lineno=node.lineno)
            #     else:
            #         name = php.Variable(node.nodes[0].name, lineno=node.lineno)
            #     initial = node.nodes[0].initial
            #     if initial is None:
            #         initial = php.Constant("None", lineno=node.lineno)
            #
            #     return py.Assign(
            #         [store(self.translate(name))], self.translate(initial), **pos(node)
            #     )

            case Stmt_Property(props=props):
                # if isinstance(node.name, (php.Variable, php.BinaryOp)):
                #     return py.Call(
                #         func=py.Name("getattr", py.Load(**pos(node)), **pos(node)),
                #         args=[self.translate(node.node), self.translate(node.name)],
                #         keywords=[],
                #         **pos(node),
                #     )
                assert False
                return py.Attribute(
                    self.translate(node.node),
                    node.name,
                    py.Load(),
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

            case Stmt_TryCatch(stmts=stmts, catches=catches, finally_=finally_):
                return py.Try(
                    body=[to_stmt(self.translate(node)) for node in stmts],
                    handlers=[],
                    #     py.ExceptHandler(
                    #         py.Name(catch.class_, py.Load(**pos(node)), **pos(node)),
                    #         store(self.translate(catches.var)),
                    #         [to_stmt(self.translate(node)) for node in catches],
                    #     )
                    #     for catch in node.catches
                    # ],
                    orelse=[],
                    finalbody=[],
                    **pos(node),
                )

            case Stmt_Throw(expr):
                return py.Raise(exc=self.translate(expr), cause=None, **pos(node))

            case _:
                debug(node)
                raise NotImplementedError(
                    f"Don't know how to translate node {node.__class__}"
                )

    def build_args(self, php_args: list[Node]):
        args = []
        kwargs = []
        for arg in php_args:
            match arg:
                case Arg(name=None, value=value):
                    args.append(self.translate(value))

                case Arg(name=name, value=value):
                    kwargs.append(py.keyword(arg=name, value=self.translate(value)))

                case _:
                    raise NotImplementedError("Should not happen")

        return args, kwargs


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
    assert name
    name.ctx = py.Store(**pos(name))
    return name


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
