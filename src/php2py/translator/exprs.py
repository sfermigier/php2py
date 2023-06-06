import ast as py

from devtools import debug

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
    Expr_StaticPropertyFetch,
    Expr_Ternary,
    Expr_UnaryOp,
    Expr_Variable,
    Node,
)

from .scalars import ScalarTranslator
from .utils import pos, store

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


class ExprTranslator(ScalarTranslator):
    def translate_expr(self, node: Node):
        match node:
            case Expr_Variable(name=name):
                if name == "this":
                    name = "self"
                return py.Name(name, py.Load())

            case Expr_ConstFetch():
                # FIXME: 'parts' should be directly addressable
                parts = node.name.get_parts()
                name = parts[0]
                match name.lower():
                    case "true":
                        return py.Name("True", py.Load())
                    case "false":
                        return py.Name("False", py.Load())
                    case "null":
                        return py.Name("None", py.Load())
                match name:
                    case "PHP_INT_MAX":
                        return py.Name("sys.maxsize", py.Load())
                    case "PHP_INT_MIN":
                        return py.Name("sys.minsize", py.Load())
                    case _:
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
                lhs = self.translate(var)
                # if not isinstance(var.name, str):
                #     debug(type(var.name), var.name, pos(node))
                #     raise ValueError("var.name is not str")

                op = binary_ops[node.op[0:-1]]()
                return py.AugAssign(
                    target=lhs,
                    op=op,
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
                    name = name.get_parts()[0]
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
                func = self.translate(class_)
                # match class_:
                #     case Expr_Variable(name):
                #
                #         pass
                #     case _:
                #         debug(class_)
                #         name = class_.get_parts()[0]
                # func = py.Name(name, py.Load())
                return py.Call(func=func, args=args, keywords=kwargs, **pos(node))

            case Expr_MethodCall(var=var, name=name, args=args):
                name = name.name
                args, kwargs = self.build_args(args)
                func = py.Attribute(value=self.translate(var), attr=name, ctx=py.Load())
                return py.Call(func=func, args=args, keywords=kwargs, **pos(node))

            case Expr_StaticCall(class_, name, args):
                class_name = class_.get_parts()[0]
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
                    debug(node)
                    raise NotImplementedError(node)
                    # return py.Name("TODO")
                    # return py.Subscript(
                    #     value=self.translate(var),
                    #     slice=py.Index(self.translate(dim)),
                    #     ctx=py.Load(),
                    #     **pos(node),
                    # )

            case Expr_ClassConstFetch(name=name, class_=class_):
                class_name = class_.get_parts()[0]
                return py.Attribute(
                    value=py.Name(id=class_name, ctx=py.Load()),
                    attr=name.name,
                    ctx=py.Load(),
                    **pos(node),
                )

            case Expr_Closure():
                # TODO
                # return py.parse("None", mode="eval")
                # debug(node, node._json)
                # Exemple
                #     node: (
                #         Expr_Closure(attrGroups=[], uses=[], byRef=False, returnType=None,
                #         stmts=[Stmt_Return(expr=Expr_MethodCall(var=Expr_Variable(name='nt'),
                #         name=Identifier(name='getPropertyDefinitions'), args=[]))],
                #         params=[
                #            Param(flags=0, attrGroups=[], default=None,
                #            byRef=False, variadic=False, var=Expr_Variable(name='nt'),
                #            type=Name(parts=[None]))
                #         ],
                #         static=False)
                #     ) (Expr_Closure)
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

            case Expr_StaticPropertyFetch(class_, name):
                class_name = class_.get_parts()[0]
                return py.Attribute(
                    value=py.Name(id=class_name, ctx=py.Load()),
                    attr=name.name,
                    ctx=py.Load(),
                    **pos(node),
                )

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
