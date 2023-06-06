import ast
import ast as py

from devtools import debug

from php2py.php_ast import (
    Expr_Yield,
    Name,
    Stmt_Break,
    Stmt_Class,
    Stmt_ClassConst,
    Stmt_ClassMethod,
    Stmt_Continue,
    Stmt_Do,
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
from php2py.py_ast import py_parse_stmt

from .exprs import ExprTranslator
from .utils import pos, to_stmt

# casts = {
#     "double": "float",
#     "string": "str",
#     "array": "list",
# }


class StmtTranslator(ExprTranslator):
    in_class: bool = False

    def translate_stmt(self, node):
        match node:
            case Stmt_Nop():
                return py.Pass(**pos(node))

            case Stmt_Echo(exprs):
                return py.Expr(
                    value=py.Call(
                        func=py.Name("print", py.Load()),
                        args=[self.translate(n) for n in exprs],
                        keywords=[],
                        **pos(node),
                    )
                )

            case Stmt_Expression(expr):
                return py.Expr(value=self.translate(expr), **pos(node))

            case Stmt_Namespace(stmts=stmts):
                return self.translate(stmts)

            case Stmt_Use(uses=uses):
                return self.translate(uses)

            case Stmt_UseUse(name, alias, type):
                parts = name.get_parts()
                if alias:
                    raise NotImplementedError("use with alias")
                else:
                    module_name = ".".join(parts)
                    return py_parse_stmt(f"from {module_name} import *")

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
                    base_class_name = base_class.get_parts()[0]
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
                    base_class_name = base_class.get_parts()[0]
                    bases.append(py.Name(base_class_name, py.Load()))

                body = [to_stmt(self.translate_stmt(stmt)) for stmt in stmts]
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

            #
            # Functions / methods
            #
            case Stmt_Function(name=name, params=params, stmts=stmts):
                args = []
                defaults = []

                if self.in_class:
                    args.append(py.Name("self", py.Param()))
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

            case Stmt_ClassMethod(name=name, params=params, stmts=stmts):
                args = []
                defaults = []
                decorator_list = []
                stmts = stmts or []

                if self.in_class:
                    args.append(py.Name("self", py.Param()))
                for param in params:
                    param_name = param.var.name
                    args.append(py.Name(param_name, py.Param()))
                    if param.default is not None:
                        defaults.append(self.translate(param.default))

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
                # TODO: switch
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

            case Stmt_Do():
                # TODO
                # Example:
                # node: (
                #     Stmt_Do(stmts=[Stmt_Expression(expr=Expr_Assign(var=Expr_ArrayDimFetch(var=Expr_PropertyFetch(var=Expr_Variable(
                #     name='this'), name=Identifier(name='linearVersions')), dim=Expr_MethodCall(var=Expr_Variable(name='version'),
                #     name=Identifier(name='getName'), args=[])), expr=Expr_Variable(name='version')))],
                #     cond=Expr_Assign(var=Expr_Variable(name='version'), expr=Expr_MethodCall(var=Expr_Variable(name='version'),
                #     name=Identifier(name='getLinearSuccessor'), args=[])))
                # ) (Stmt_Do)
                return py.Pass()

            case _:
                debug(node)
                raise NotImplementedError(
                    f"Don't know how to translate node {node.__class__}"
                )
