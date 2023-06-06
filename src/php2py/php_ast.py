from __future__ import annotations

from typing import Any

from attr import dataclass

frozen = dataclass


@frozen
class Node:
    def __getitem__(self, item):
        if item == "nodeType":
            return self.__class__.__name__
        raise KeyError(item)

    @property
    def _lineno(self):
        return self._json["attributes"]["startLine"]

    @property
    def _col_offset(self):
        return 0
        # return self._attributes["col_offset"]

    def get_parts(self):
        return self._json["parts"]


@frozen
class Expr(Node):
    pass


@frozen
class Stmt(Node):
    pass


@frozen
class Scalar(Node):
    pass


@frozen
class Arg(Node):
    name: Identifier | None
    value: Expr
    byRef: int
    unpack: int


@frozen
class Attribute(Node):
    name: Name | Name_FullyQualified
    args: list[Node] | list[Stmt]


@frozen
class AttributeGroup(Node):
    attrs: list[Node]


@frozen
class Const(Node):
    namespacedName: None
    name: Identifier
    value: Expr | Scalar_DNumber | Scalar_LNumber | Scalar_String


@frozen
class Expr_Array(Expr):
    items: list[Any] | list[Expr] | list[Stmt]


@frozen
class Expr_ArrayDimFetch(Expr):
    var: Expr
    dim: Expr | None | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Function | Scalar_String


@frozen
class Expr_ArrayItem(Expr):
    byRef: int
    unpack: int
    key: Expr | None | Scalar_Encapsed | Scalar_LNumber | Scalar_String
    value: Expr | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Class | Scalar_MagicConst_Dir | Scalar_MagicConst_File | Scalar_MagicConst_Function | Scalar_String


@frozen
class Expr_ArrowFunction(Expr):
    expr: Expr | Scalar_Encapsed
    attrGroups: list[Stmt]
    byRef: int
    returnType: Identifier | Name | None | NullableType
    params: list[Node] | list[Stmt]
    static: int


@frozen
class Expr_Assign(Expr):
    var: Expr
    expr: Expr | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Dir | Scalar_MagicConst_File | Scalar_String


@frozen
class Expr_AssignOp(Expr):
    """Abstract base class."""

    var: Expr
    expr: Expr


@frozen
class Expr_AssignOp_BitwiseAnd(Expr_AssignOp):
    op = "&="


@frozen
class Expr_AssignOp_BitwiseOr(Expr_AssignOp):
    op = "|="


@frozen
class Expr_AssignOp_BitwiseXor(Expr_AssignOp):
    op = "^="


@frozen
class Expr_AssignOp_Coalesce(Expr_AssignOp):
    op = "??="


@frozen
class Expr_AssignOp_Concat(Expr_AssignOp):
    op = ".="


@frozen
class Expr_AssignOp_Div(Expr_AssignOp):
    op = "/="


@frozen
class Expr_AssignOp_Minus(Expr_AssignOp):
    op = "-="


@frozen
class Expr_AssignOp_Mul(Expr_AssignOp):
    op = "*="


@frozen
class Expr_AssignOp_Plus(Expr_AssignOp):
    op = "+="


@frozen
class Expr_AssignOp_ShiftRight(Expr_AssignOp):
    op = ">>="


@frozen
class Expr_AssignRef(Expr):
    var: Expr
    expr: Expr


#
# Binary ops
#
@frozen
class Expr_BinaryOp(Expr):
    """Abstract base class for all binary ops."""

    left: Expr
    right: Expr


@frozen
class Expr_BinaryOp_BitwiseAnd(Expr_BinaryOp):
    op = "&"


@frozen
class Expr_BinaryOp_BitwiseOr(Expr_BinaryOp):
    op = "|"


@frozen
class Expr_BinaryOp_BitwiseXor(Expr_BinaryOp):
    op = "^"


@frozen
class Expr_BinaryOp_BooleanAnd(Expr_BinaryOp):
    op = "&&"


@frozen
class Expr_BinaryOp_BooleanOr(Expr_BinaryOp):
    op = "||"


@frozen
class Expr_BinaryOp_Coalesce(Expr_BinaryOp):
    op = "??"


@frozen
class Expr_BinaryOp_Concat(Expr_BinaryOp):
    op = "."
    pass


@frozen
class Expr_BinaryOp_Div(Expr_BinaryOp):
    op = "/"


@frozen
class Expr_BinaryOp_Equal(Expr_BinaryOp):
    op = "=="


@frozen
class Expr_BinaryOp_Greater(Expr_BinaryOp):
    op = ">"


@frozen
class Expr_BinaryOp_GreaterOrEqual(Expr_BinaryOp):
    op = ">="


@frozen
class Expr_BinaryOp_Identical(Expr_BinaryOp):
    op = "==="


@frozen
class Expr_BinaryOp_LogicalAnd(Expr_BinaryOp):
    op = "???"


@frozen
class Expr_BinaryOp_LogicalOr(Expr_BinaryOp):
    op = "???"


@frozen
class Expr_BinaryOp_LogicalXor(Expr_BinaryOp):
    op = "???"


@frozen
class Expr_BinaryOp_Minus(Expr_BinaryOp):
    op = "-"


@frozen
class Expr_BinaryOp_Mod(Expr_BinaryOp):
    op = "%"


@frozen
class Expr_BinaryOp_Mul(Expr_BinaryOp):
    op = "*"


@frozen
class Expr_BinaryOp_NotEqual(Expr_BinaryOp):
    op = "!="


@frozen
class Expr_BinaryOp_NotIdentical(Expr_BinaryOp):
    op = "!=="


@frozen
class Expr_BinaryOp_Plus(Expr_BinaryOp):
    op = "+"


@frozen
class Expr_BinaryOp_Pow(Expr_BinaryOp):
    op = "**"


@frozen
class Expr_BinaryOp_ShiftLeft(Expr_BinaryOp):
    op = "<<"


@frozen
class Expr_BinaryOp_ShiftRight(Expr_BinaryOp):
    op = ">>"


@frozen
class Expr_BinaryOp_Smaller(Expr_BinaryOp):
    op = "<"


@frozen
class Expr_BinaryOp_SmallerOrEqual(Expr_BinaryOp):
    op = "<="


@frozen
class Expr_BinaryOp_Spaceship(Expr_BinaryOp):
    op = "???"


#
# Unary ops
#
@frozen
class Expr_UnaryOp(Expr):
    expr: Expr


@frozen
class Expr_UnaryMinus(Expr_UnaryOp):
    op = "-"


@frozen
class Expr_UnaryPlus(Expr_UnaryOp):
    op = "+"


@frozen
class Expr_BitwiseNot(Expr_UnaryOp):
    op = "~"


@frozen
class Expr_BooleanNot(Expr_UnaryOp):
    op = "!"


#
# Casts
#
@frozen
class Expr_Cast(Expr):
    expr: Expr


@frozen
class Expr_Cast_Array(Expr_Cast):
    cast = "TODO"


@frozen
class Expr_Cast_Bool(Expr_Cast):
    cast = "bool"


@frozen
class Expr_Cast_Double(Expr_Cast):
    cast = "float"


@frozen
class Expr_Cast_Int(Expr_Cast):
    cast = "int"


@frozen
class Expr_Cast_Object(Expr_Cast):
    cast = "TODO"


@frozen
class Expr_Cast_String(Expr_Cast):
    cast = "str"


@frozen
class Expr_ClassConstFetch(Expr):
    name: Identifier
    class_: Expr | Name | Name_FullyQualified


@frozen
class Expr_Clone(Expr):
    expr: Expr


@frozen
class Expr_Closure(Expr):
    attrGroups: list[Stmt]
    uses: list[Expr] | list[Stmt]
    byRef: int
    returnType: Identifier | Name | Name_FullyQualified | None | NullableType | UnionType
    stmts: list[Stmt]
    params: list[Node] | list[Stmt]
    static: int


@frozen
class Expr_ClosureUse(Expr):
    var: Expr
    byRef: int


@frozen
class Expr_ConstFetch(Expr):
    name: Name | Name_FullyQualified


@frozen
class Expr_Empty(Expr):
    expr: Expr


@frozen
class Expr_ErrorSuppress(Expr):
    expr: Expr


@frozen
class Expr_Eval(Expr):
    expr: Expr | Scalar_String


@frozen
class Expr_Exit(Expr):
    expr: Expr | None | Scalar_Encapsed | Scalar_LNumber | Scalar_String


@frozen
class Expr_FuncCall(Expr):
    name: Expr | Name | Name_FullyQualified
    args: list[Node] | list[Stmt]


@frozen
class Expr_Include(Expr):
    expr: Expr | Scalar_Encapsed | Scalar_String
    type: int


@frozen
class Expr_Instanceof(Expr):
    expr: Expr
    class_: Expr | Name | Name_FullyQualified


@frozen
class Expr_Isset(Expr):
    vars: list[Expr]


@frozen
class Expr_List(Expr):
    items: list[Any] | list[Expr]


@frozen
class Expr_Match(Expr):
    cond: Expr | Scalar_DNumber
    arms: list[Node]


@frozen
class Expr_MethodCall(Expr):
    var: Expr
    name: Expr | Identifier | Scalar_Encapsed | Scalar_MagicConst_Class | Scalar_MagicConst_Function
    args: list[Node] | list[Stmt]


@frozen
class Expr_New(Expr):
    class_: Expr | Name | Name_FullyQualified | Stmt_Class
    args: list[Node] | list[Stmt]


@frozen
class Expr_NullsafeMethodCall(Expr):
    var: Expr
    name: Identifier
    args: list[Node] | list[Stmt]


@frozen
class Expr_NullsafePropertyFetch(Expr):
    var: Expr
    name: Identifier


@frozen
class Expr_PostDec(Expr):
    var: Expr


@frozen
class Expr_PostInc(Expr):
    var: Expr


@frozen
class Expr_PreDec(Expr):
    var: Expr


@frozen
class Expr_PreInc(Expr):
    var: Expr


@frozen
class Expr_Print(Expr):
    expr: Scalar_String


@frozen
class Expr_PropertyFetch(Expr):
    var: Expr
    name: Expr | Identifier | Scalar_String


@frozen
class Expr_ShellExec(Expr):
    parts: list[Node]


@frozen
class Expr_StaticCall(Expr):
    class_: Expr | Name | Name_FullyQualified
    name: Expr | Identifier | Scalar_MagicConst_Class
    args: list[Node] | list[Stmt]


@frozen
class Expr_StaticPropertyFetch(Expr):
    class_: Expr | Name | Scalar_String
    name: Expr | VarLikeIdentifier


@frozen
class Expr_Ternary(Expr):
    if_: Expr | None | Scalar_Encapsed | Scalar_LNumber | Scalar_String
    cond: Expr
    else_: Expr | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_String


@frozen
class Expr_Throw(Expr):
    expr: Expr


@frozen
class Expr_Variable(Expr):
    name: Expr | str


@frozen
class Expr_Yield(Expr):
    key: Expr | None | Scalar_String
    value: Expr | Scalar_LNumber | Scalar_String


@frozen
class Expr_YieldFrom(Expr):
    expr: Expr


@frozen
class Identifier(Node):
    name: str


@frozen
class MatchArm(Node):
    conds: None | list[Expr] | list[Scalar]
    body: Expr | Scalar_LNumber | Scalar_String


@frozen
class Name(Node):
    parts: list[str]


@frozen
class Name_FullyQualified(Node):
    parts: list[str]


@frozen
class Name_Relative(Node):
    parts: list[str]


@frozen
class NullableType(Node):
    type: Identifier | Name | Name_FullyQualified


@frozen
class Param(Node):
    flags: int
    attrGroups: list[Stmt]
    default: Expr | None | Scalar_DNumber | Scalar_LNumber | Scalar_String
    byRef: int
    variadic: int
    var: Expr
    type: Identifier | Name | Name_FullyQualified | None | NullableType | UnionType


@frozen
class Scalar_DNumber(Scalar):
    value: float | int


@frozen
class Scalar_Encapsed(Scalar):
    parts: list[Expr] | list[Node]


@frozen
class Scalar_EncapsedStringPart(Scalar):
    value: str


@frozen
class Scalar_LNumber(Scalar):
    value: int


@frozen
class Scalar_MagicConst_Class(Scalar):
    pass


@frozen
class Scalar_MagicConst_Dir(Scalar):
    pass


@frozen
class Scalar_MagicConst_File(Scalar):
    pass


@frozen
class Scalar_MagicConst_Function(Scalar):
    pass


@frozen
class Scalar_MagicConst_Line(Scalar):
    pass


@frozen
class Scalar_MagicConst_Method(Scalar):
    pass


@frozen
class Scalar_MagicConst_Namespace(Scalar):
    pass


@frozen
class Scalar_String(Scalar):
    value: str


@frozen
class Stmt_Break(Stmt):
    num: None | Scalar_LNumber


@frozen
class Stmt_Case(Stmt):
    cond: Expr | None | Scalar_LNumber | Scalar_String
    stmts: list[Stmt]


@frozen
class Stmt_Catch(Stmt):
    var: Expr
    types: list[Node]
    stmts: list[Stmt]


@frozen
class Stmt_Class(Stmt):
    attrGroups: list[Stmt]
    flags: int
    extends: Name | Name_FullyQualified | None
    implements: list[Node] | list[Stmt]
    namespacedName: None
    stmts: list[Stmt]
    name: Identifier | None


@frozen
class Stmt_ClassConst(Stmt):
    flags: int
    attrGroups: list[Stmt]
    consts: list[Node]


@frozen
class Stmt_ClassMethod(Stmt):
    name: Identifier
    params: list[Node] | list[Stmt]
    stmts: None | list[Stmt]
    flags: int
    attrGroups: list[Node] | list[Stmt]
    byRef: int
    returnType: Identifier | Name | Name_FullyQualified | None | NullableType | UnionType


@frozen
class Stmt_Const(Stmt):
    consts: list[Node]


@frozen
class Stmt_Continue(Stmt):
    num: None | Scalar_LNumber


@frozen
class Stmt_Declare(Stmt):
    stmts: None
    declares: list[Stmt]


@frozen
class Stmt_DeclareDeclare(Stmt):
    key: Identifier
    value: Scalar_LNumber


@frozen
class Stmt_Do(Stmt):
    stmts: list[Stmt]
    cond: Expr | Scalar_LNumber


@frozen
class Stmt_Echo(Stmt):
    exprs: list[Expr] | list[Node] | list[Scalar]


@frozen
class Stmt_Else(Stmt):
    stmts: list[Stmt]


@frozen
class Stmt_ElseIf(Stmt):
    cond: Expr
    stmts: list[Stmt]


@frozen
class Stmt_Enum(Stmt):
    attrGroups: list[Stmt]
    scalarType: Identifier | None
    implements: list[Stmt]
    namespacedName: None
    stmts: list[Stmt]
    name: Identifier


@frozen
class Stmt_EnumCase(Stmt):
    expr: None | Scalar_LNumber | Scalar_String
    attrGroups: list[Stmt]
    name: Identifier


@frozen
class Stmt_Expression(Stmt):
    expr: Expr


@frozen
class Stmt_Finally(Stmt):
    stmts: list[Stmt]


@frozen
class Stmt_For(Stmt):
    init: list[Expr] | list[Stmt]
    loop: list[Expr] | list[Stmt]
    cond: list[Expr] | list[Stmt]
    stmts: list[Stmt]


@frozen
class Stmt_Foreach(Stmt):
    expr: Expr
    valueVar: Expr
    stmts: list[Stmt]
    byRef: int
    keyVar: Expr | None


@frozen
class Stmt_Function(Stmt):
    name: Identifier
    params: list[Node] | list[Stmt]
    stmts: list[Stmt]
    attrGroups: list[Stmt]
    byRef: int
    returnType: Identifier | Name | None | NullableType
    namespacedName: None


@frozen
class Stmt_Global(Stmt):
    vars: list[Expr]


@frozen
class Stmt_Goto(Stmt):
    name: Identifier


@frozen
class Stmt_GroupUse(Stmt):
    uses: list[Stmt]
    type: int
    prefix: Name


@frozen
class Stmt_If(Stmt):
    cond: Expr | Scalar_LNumber
    stmts: list[Stmt]
    elseifs: list[Stmt]
    else_: None | Stmt_Else


@frozen
class Stmt_InlineHTML(Stmt):
    value: str


@frozen
class Stmt_Interface(Stmt):
    attrGroups: list[Stmt]
    extends: list[Node] | list[Stmt]
    namespacedName: None
    stmts: list[Stmt]
    name: Identifier


@frozen
class Stmt_Label(Stmt):
    name: Identifier


@frozen
class Stmt_Namespace(Stmt):
    stmts: list[Stmt]
    name: Name | None


@frozen
class Stmt_Nop(Stmt):
    pass


@frozen
class Stmt_Property(Stmt):
    props: list[Stmt]
    flags: int
    attrGroups: list[Stmt]
    type: Identifier | Name | Name_FullyQualified | None | NullableType | UnionType


@frozen
class Stmt_PropertyProperty(Stmt):
    name: VarLikeIdentifier
    default: Expr | None | Scalar_LNumber | Scalar_String


@frozen
class Stmt_Return(Stmt):
    expr: Expr | None | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Dir | Scalar_String


@frozen
class Stmt_Static(Stmt):
    vars: list[Stmt]


@frozen
class Stmt_StaticVar(Stmt):
    var: Expr
    default: Expr | None | Scalar_LNumber | Scalar_String


@frozen
class Stmt_Switch(Stmt):
    cases: list[Stmt]
    cond: Expr


@frozen
class Stmt_Throw(Stmt):
    expr: Expr


@frozen
class Stmt_Trait(Stmt):
    attrGroups: list[Stmt]
    namespacedName: None
    stmts: list[Stmt]
    name: Identifier


@frozen
class Stmt_TraitUse(Stmt):
    adaptations: list[Stmt]
    traits: list[Node]


@frozen
class Stmt_TraitUseAdaptation_Alias(Stmt):
    newModifier: None | int
    newName: Identifier
    method: Identifier
    trait: Name | None


@frozen
class Stmt_TryCatch(Stmt):
    stmts: list[Stmt]
    catches: list[Stmt]
    finally_: None | Stmt_Finally


@frozen
class Stmt_Unset(Stmt):
    vars: list[Expr]


@frozen
class Stmt_Use(Stmt):
    uses: list[Stmt]
    type: int


@frozen
class Stmt_UseUse(Stmt):
    name: Name
    alias: Identifier | None
    type: int


@frozen
class Stmt_While(Stmt):
    cond: Expr | Scalar_LNumber
    stmts: list[Stmt]


@frozen
class UnionType(Node):
    types: list[Node]


@frozen
class VarLikeIdentifier(Node):
    name: str
