#!/usr/bin/env python
import ast
import ast as py
import sys
from dataclasses import dataclass
from types import NoneType

from devtools import debug

from php2py.ast_utils import print_ast
from php2py.php_ast import (
    Arg,
    Expr_Array,
    Expr_ArrayDimFetch,
    Expr_Assign,
    Expr_AssignOp,
    Expr_AssignOp_Coalesce,
    Expr_AssignRef,
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
    Expr_Instanceof,
    Expr_Isset,
    Expr_List,
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
    Expr_Yield,
    Name,
    Node,
    Scalar_DNumber,
    Scalar_Encapsed,
    Scalar_EncapsedStringPart,
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
    Stmt_InlineHTML,
    Stmt_Interface,
    Stmt_Namespace,
    Stmt_Nop,
    Stmt_Property,
    Stmt_Return,
    Stmt_Static,
    Stmt_Switch,
    Stmt_Throw,
    Stmt_TryCatch,
    Stmt_Unset,
    Stmt_Use,
    Stmt_UseUse,
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


@dataclass
class Translator:
    in_class: bool = False

    def translate_root(self, root_node):
        return py.Module(body=[self.translate(n) for n in root_node], type_ignores=[])

    def translate(self, node):
        # debug(node)
        match node:
            case [*_]:
                return [self.translate(n) for n in node]

            case Node():
                node_type = node.__class__.__name__

                if node_type.startswith("Scalar_"):
                    return self.translate_scalar(node)

                if node_type.startswith("Expr_"):
                    return self.translate_expr(node)

                if node_type.startswith("Stmt_"):
                    return self.translate_stmt(node)

                if node_type == "Name":
                    parts = node._json["parts"]
                    name = parts[0]
                    return py.Name(name, py.Load())

                return self.translate_other(node)

            case _:
                # TODO
                return py.parse("None")
                # debug(node)
                # assert False

    def translate_other(self, node):
        debug(node)
        raise NotImplementedError()

    def translate_scalar(self, node):
        match node:
            case Scalar_String(value=value):
                return py.Str(value)

            case Scalar_LNumber(value=value):
                return py.Num(value)

            case Scalar_DNumber(value=value):
                return py.Num(value)

            case Scalar_Encapsed():
                return self.translate_encapsed(node)

            case _:
                debug(node)
                raise NotImplementedError()

    def translate_encapsed(self, node):
        parts = node.parts
        result = []
        for part in parts:
            match part:
                case Scalar_EncapsedStringPart(value=value):
                    result.append(value)
                case Expr_Variable(name=name):
                    result.append("{name}")
                case _:
                    debug(part)
                    raise NotImplementedError()
        return py.Str("".join(result))

    def translate_expr(self, node):
        match node:
            case Expr_Variable(name=name):
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
            case Expr_UnaryOp(expr=expr):
                op = unary_ops[node.op]()
                return py.UnaryOp(op, self.translate(expr))

            #
            # Binary ops
            #
            case Expr_BinaryOp(left=left, right=right):
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
                    # TODO
                    # return py.parse("None")
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
                    Expr_Cast_Object: "TODO_cast_object",
                    Expr_Cast_Array: "TODO_cast_array",
                    Expr_Cast_Bool: "bool",
                    Expr_Cast_Double: "float",
                    Expr_Cast_Int: "int",
                    Expr_Cast_String: "str",
                }.get(node.__class__)

                return py.Call(
                    func=py.Name(cast_name, py.Load()),
                    args=[self.translate(expr)],
                    keywords=[],
                )

            #
            # Assign ops
            #
            case Expr_AssignRef():
                raise NotImplementedError()
                # return f"""{self.parse(node['var'])} = {self.parse(node['expr'])}"""

            case Expr_AssignOp_Coalesce():
                raise NotImplementedError()
                # # TODO
                # lhs = self.parse(node['var'])
                # rhs = self.parse(node['expr'])
                # return f"""{lhs} = {lhs} if {lhs} is not None else {rhs}"""

            case Expr_AssignOp(var=var, expr=expr):
                assert isinstance(var.name, str)
                op = binary_ops[node.op[0:-1]]()
                return py.AugAssign(
                    target=py.Name(id=var.name, ctx=py.Store()),
                    op=py.Add(),
                    value=self.translate(expr),
                    **pos(node),
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
                return py.Attribute(
                    value=self.translate(var), attr=name, ctx=py.Load(), **pos(node)
                )

            case Expr_Isset(vars):
                debug(vars)
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
                if hasattr(name, "name"):
                    name = name.name
                else:
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
                    return py.Name("TODO")
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
                # TODO
                # return py.parse("None", mode="eval")
                debug(node, node._json)
                raise NotImplementedError(node.__class__.__name__)

            case Expr_List(items):
                return py.List(
                    elts=[self.translate(item) for item in items],
                    ctx=py.Store(),
                )

            case Expr_Instanceof(expr, class_):
                return py.Call(
                    func=py.Name("isinstance", py.Load()),
                    args=[self.translate(expr), self.translate(class_)],
                    keywords=[],
                )

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

            case Stmt_UseUse():
                # TODO
                return py.Pass

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
                            test=self.translate(elseif.cond),
                            body=[
                                to_stmt(self.translate(stmt)) for stmt in elseif.stmts
                            ],
                            orelse=orelse,
                        )
                    ]

                return py.If(
                    test=self.translate(cond),
                    body=[to_stmt(self.translate(stmt)) for stmt in stmts],
                    orelse=orelse,
                    **pos(node),
                )

            case Stmt_For(init, loop, cond, stmts):
                assert (
                    cond is None or len(cond) == 1
                ), "only a single test is supported in for-loops"

                test = self.translate(cond[0])
                body = [
                    to_stmt(n) for n in self.translate(stmts) + [self.translate(loop)]
                ]
                return self.translate(init) + [
                    py.While(
                        test=test,
                        body=body,
                        orelse=[],
                    ),
                ]

                # return from_phpast(
                #     php.Block(
                #         (node.start or [])
                #         + [
                #             php.While(
                #                 node.test[0] if node.test else 1,
                #                 php.Block(
                #                     deblock(node.node) + (node.count or []),
                #                     lineno=node.lineno,
                #                 ),
                #                 lineno=node.lineno,
                #             )
                #         ],
                #         lineno=node.lineno,
                #     )
                # )

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
                if self.in_class:
                    args.append(py.Name("self", py.Param()))
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

            case Expr_Yield(key=key, value=value):
                # TODO: what do we do with 'key' ?
                if value is None:
                    return py.Yield(None)
                else:
                    return py.Yield(self.translate(value))

            #
            # Class definitions
            #
            case Stmt_Class(name=name, stmts=stmts, extends=extends):
                self.in_class = True
                name = name.name

                if extends is None:
                    extends = []
                if isinstance(extends, Name):
                    extends = [extends]
                bases = []
                for base_class in extends:
                    base_class_name = base_class._json["parts"][0]
                    bases.append(py.Name(base_class_name, py.Load()))

                body = [to_stmt(self.translate(stmt)) for stmt in stmts]
                for stmt in body:
                    if isinstance(stmt, py.FunctionDef) and stmt.name in (
                        name,
                        "__construct",
                    ):
                        stmt.name = "__init__"
                if not body:
                    body = [py.Pass()]

                self.in_class = False
                return py.ClassDef(
                    name=name,
                    bases=bases,
                    keywords=[],
                    body=body,
                    decorator_list=[],
                )

            case Stmt_Interface(name=name, stmts=stmts, extends=extends):
                # Example node: (
                #     Stmt_Interface(attrGroups=[], extends=[], namespacedName=None, stmts=[],
                #     name=Identifier(name='CredentialsInterface'))
                # )
                # debug(node)
                self.in_class = True

                name = name.name
                if extends is None:
                    extends = []
                if isinstance(extends, Name):
                    extends = [extends]
                bases = []
                for base_class in extends:
                    debug(base_class)
                    base_class_name = base_class._json["parts"][0]
                    bases.append(py.Name(base_class_name, py.Load()))

                body = [to_stmt(self.translate(stmt)) for stmt in stmts]
                for stmt in body:
                    if isinstance(stmt, py.FunctionDef) and stmt.name in (
                        name,
                        "__construct",
                    ):
                        stmt.name = "__init__"
                if not body:
                    body = [py.Pass()]

                self.in_class = False
                return py.ClassDef(
                    name=name,
                    bases=bases,
                    keywords=[],
                    body=body,
                    decorator_list=[],
                )

            case Stmt_ClassConst():
                # TODO
                return py.Pass

            case Stmt_ClassMethod(name=name, params=params, stmts=stmts):
                # debug(node)
                args = []
                defaults = []
                decorator_list = []
                stmts = stmts or []

                # decorator_list.append(py.Name("classmethod", py.Load()))
                args.append(py.Name("self", py.Param()))

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

            case Stmt_Switch():
                debug()
                print_ast(node)
                return ast.Pass()

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
                # TODO
                return py.Pass()
                # # if isinstance(node.name, (php.Variable, php.BinaryOp)):
                # #     return py.Call(
                # #         func=py.Name("getattr", py.Load(**pos(node)), **pos(node)),
                # #         args=[self.translate(node.node), self.translate(node.name)],
                # #         keywords=[],
                # #         **pos(node),
                # #     )
                #
                # assert len(props) == 1
                # prop = props[0]
                # return py.Attribute(
                #     self.translate(node.node),
                #     node.name,
                #     py.Load(),
                #     **pos(node),
                # )

            #
            # Exceptions
            #
            case Stmt_TryCatch(stmts=stmts, catches=catches, finally_=finally_):
                # handlers = [
                #     py.ExceptHandler(
                #         py.Name(catch.class_, py.Load(**pos(node)), **pos(node)),
                #         store(self.translate(catches.var)),
                #         [to_stmt(self.translate(node)) for node in catches],
                #     )
                #     for catch in node.catches
                # ]
                handlers = [
                    py.ExceptHandler(
                        py.Name("Exception", py.Load()),
                        None,
                        [py.Pass()],
                    )
                ]

                return py.Try(
                    body=[to_stmt(self.translate(node)) for node in stmts],
                    handlers=handlers,
                    orelse=[],
                    finalbody=[],
                    **pos(node),
                )

            case Stmt_Throw(expr):
                return py.Raise(exc=self.translate(expr), cause=None, **pos(node))

            case Stmt_Static():
                # TODO
                return py.Pass()

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
