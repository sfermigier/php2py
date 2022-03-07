from __future__ import annotations

from typing import Any

from attr import define


@define
class Node:

    def __getitem__(self, item):
        if item == "nodeType":
            return self.__class__.__name__
        raise KeyError(item)


@define
class Expr(Node):
    pass


@define
class Stmt(Node):
    pass


@define
class Scalar(Node):
    pass


@define
class Arg(Node):
    byRef: int
    unpack: int
    name: Identifier | None
    value: Expr | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Class | Scalar_MagicConst_Dir | Scalar_MagicConst_File | Scalar_MagicConst_Function | Scalar_MagicConst_Line | Scalar_MagicConst_Method | Scalar_String


@define
class Attribute(Node):
    name: Name | Name_FullyQualified
    args: list[Node] | list[Stmt]


@define
class AttributeGroup(Node):
    attrs: list[Node]


@define
class Const(Node):
    namespacedName: None
    name: Identifier
    value: Expr | Scalar_DNumber | Scalar_LNumber | Scalar_String


@define
class Expr_Array(Expr):
    items: list[Any] | list[Expr] | list[Stmt]


@define
class Expr_ArrayDimFetch(Expr):
    var: Expr
    dim: Expr | None | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Function | Scalar_String


@define
class Expr_ArrayItem(Expr):
    byRef: int
    unpack: int
    key: Expr | None | Scalar_Encapsed | Scalar_LNumber | Scalar_String
    value: Expr | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Class | Scalar_MagicConst_Dir | Scalar_MagicConst_File | Scalar_MagicConst_Function | Scalar_String


@define
class Expr_ArrowFunction(Expr):
    expr: Expr | Scalar_Encapsed
    attrGroups: list[Stmt]
    byRef: int
    returnType: Identifier | Name | None | NullableType
    params: list[Node] | list[Stmt]
    static: int


@define
class Expr_Assign(Expr):
    expr: Expr | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Dir | Scalar_MagicConst_File | Scalar_String
    var: Expr


@define
class Expr_AssignOp_BitwiseAnd(Expr):
    expr: Expr
    var: Expr


@define
class Expr_AssignOp_BitwiseOr(Expr):
    expr: Expr
    var: Expr


@define
class Expr_AssignOp_Coalesce(Expr):
    expr: Expr
    var: Expr


@define
class Expr_AssignOp_Concat(Expr):
    expr: Expr | Scalar_Encapsed | Scalar_String
    var: Expr


@define
class Expr_AssignOp_Div(Expr):
    expr: Expr | Scalar_LNumber
    var: Expr


@define
class Expr_AssignOp_Minus(Expr):
    expr: Expr | Scalar_LNumber
    var: Expr


@define
class Expr_AssignOp_Mul(Expr):
    expr: Expr | Scalar_LNumber
    var: Expr


@define
class Expr_AssignOp_Plus(Expr):
    expr: Expr | Scalar_DNumber | Scalar_LNumber
    var: Expr


@define
class Expr_AssignOp_ShiftRight(Expr):
    expr: Scalar_LNumber
    var: Expr


@define
class Expr_AssignRef(Expr):
    expr: Expr
    var: Expr


@define
class Expr_BinaryOp_BitwiseAnd(Expr):
    right: Expr | Scalar_LNumber
    left: Expr


@define
class Expr_BinaryOp_BitwiseOr(Expr):
    right: Expr | Scalar_LNumber
    left: Expr


@define
class Expr_BinaryOp_BitwiseXor(Expr):
    right: Expr
    left: Expr


@define
class Expr_BinaryOp_BooleanAnd(Expr):
    right: Expr
    left: Expr | Scalar_String


@define
class Expr_BinaryOp_BooleanOr(Expr):
    right: Expr
    left: Expr


@define
class Expr_BinaryOp_Coalesce(Expr):
    right: Expr | Scalar_LNumber | Scalar_String
    left: Expr | Scalar_String


@define
class Expr_BinaryOp_Concat(Expr):
    right: Expr | Scalar_Encapsed | Scalar_MagicConst_Class | Scalar_MagicConst_Dir | Scalar_MagicConst_Function | Scalar_MagicConst_Line | Scalar_String
    left: Expr | Scalar_Encapsed | Scalar_MagicConst_Dir | Scalar_MagicConst_Function | Scalar_MagicConst_Method | Scalar_MagicConst_Namespace | Scalar_String


@define
class Expr_BinaryOp_Div(Expr):
    right: Expr | Scalar_DNumber | Scalar_LNumber
    left: Expr | Scalar_LNumber


@define
class Expr_BinaryOp_Equal(Expr):
    right: Expr | Scalar_Encapsed | Scalar_LNumber | Scalar_String
    left: Expr | Scalar_Encapsed | Scalar_LNumber | Scalar_String


@define
class Expr_BinaryOp_Greater(Expr):
    right: Expr | Scalar_DNumber | Scalar_LNumber | Scalar_String
    left: Expr


@define
class Expr_BinaryOp_GreaterOrEqual(Expr):
    right: Expr | Scalar_DNumber | Scalar_LNumber | Scalar_String
    left: Expr


@define
class Expr_BinaryOp_Identical(Expr):
    right: Expr | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_String
    left: Expr | Scalar_LNumber | Scalar_String


@define
class Expr_BinaryOp_LogicalAnd(Expr):
    right: Expr
    left: Expr


@define
class Expr_BinaryOp_LogicalOr(Expr):
    right: Expr
    left: Expr


@define
class Expr_BinaryOp_LogicalXor(Expr):
    right: Expr
    left: Expr


@define
class Expr_BinaryOp_Minus(Expr):
    right: Expr | Scalar_LNumber
    left: Expr | Scalar_LNumber


@define
class Expr_BinaryOp_Mod(Expr):
    right: Expr | Scalar_LNumber
    left: Expr


@define
class Expr_BinaryOp_Mul(Expr):
    right: Expr | Scalar_DNumber | Scalar_LNumber
    left: Expr | Scalar_DNumber | Scalar_LNumber


@define
class Expr_BinaryOp_NotEqual(Expr):
    right: Expr | Scalar_LNumber | Scalar_String
    left: Expr | Scalar_LNumber | Scalar_String


@define
class Expr_BinaryOp_NotIdentical(Expr):
    right: Expr | Scalar_LNumber | Scalar_String
    left: Expr | Scalar_LNumber | Scalar_String


@define
class Expr_BinaryOp_Plus(Expr):
    right: Expr | Scalar_DNumber | Scalar_LNumber
    left: Expr | Scalar_DNumber | Scalar_LNumber


@define
class Expr_BinaryOp_Pow(Expr):
    right: Expr
    left: Expr


@define
class Expr_BinaryOp_ShiftLeft(Expr):
    right: Expr | Scalar_LNumber
    left: Expr | Scalar_LNumber


@define
class Expr_BinaryOp_ShiftRight(Expr):
    right: Expr | Scalar_LNumber
    left: Expr


@define
class Expr_BinaryOp_Smaller(Expr):
    right: Expr | Scalar_DNumber | Scalar_LNumber | Scalar_String
    left: Expr | Scalar_LNumber


@define
class Expr_BinaryOp_SmallerOrEqual(Expr):
    right: Expr | Scalar_DNumber | Scalar_LNumber
    left: Expr | Scalar_LNumber


@define
class Expr_BinaryOp_Spaceship(Expr):
    right: Expr | Scalar_DNumber | Scalar_LNumber | Scalar_String
    left: Expr | Scalar_DNumber | Scalar_LNumber | Scalar_String


@define
class Expr_BitwiseNot(Expr):
    expr: Expr | Scalar_LNumber


@define
class Expr_BooleanNot(Expr):
    expr: Expr


@define
class Expr_Cast_Array(Expr):
    expr: Expr


@define
class Expr_Cast_Bool(Expr):
    expr: Expr


@define
class Expr_Cast_Double(Expr):
    expr: Expr


@define
class Expr_Cast_Int(Expr):
    expr: Expr


@define
class Expr_Cast_Object(Expr):
    expr: Expr


@define
class Expr_Cast_String(Expr):
    expr: Expr


@define
class Expr_ClassConstFetch(Expr):
    class_: Expr | Name | Name_FullyQualified
    name: Identifier


@define
class Expr_Clone(Expr):
    expr: Expr


@define
class Expr_Closure(Expr):
    attrGroups: list[Stmt]
    uses: list[Expr] | list[Stmt]
    byRef: int
    returnType: Identifier | Name | Name_FullyQualified | None | NullableType | UnionType
    stmts: list[Stmt]
    params: list[Node] | list[Stmt]
    static: int


@define
class Expr_ClosureUse(Expr):
    byRef: int
    var: Expr


@define
class Expr_ConstFetch(Expr):
    name: Name | Name_FullyQualified


@define
class Expr_Empty(Expr):
    expr: Expr


@define
class Expr_ErrorSuppress(Expr):
    expr: Expr


@define
class Expr_Eval(Expr):
    expr: Expr | Scalar_String


@define
class Expr_Exit(Expr):
    expr: Expr | None | Scalar_Encapsed | Scalar_LNumber | Scalar_String


@define
class Expr_FuncCall(Expr):
    name: Expr | Name | Name_FullyQualified
    args: list[Node] | list[Stmt]


@define
class Expr_Include(Expr):
    expr: Expr | Scalar_Encapsed | Scalar_String
    type: int


@define
class Expr_Instanceof(Expr):
    expr: Expr
    class_: Expr | Name | Name_FullyQualified


@define
class Expr_Isset(Expr):
    vars: list[Expr]


@define
class Expr_List(Expr):
    items: list[Any] | list[Expr]


@define
class Expr_Match(Expr):
    cond: Expr | Scalar_DNumber
    arms: list[Node]


@define
class Expr_MethodCall(Expr):
    var: Expr
    name: Expr | Identifier | Scalar_Encapsed | Scalar_MagicConst_Class | Scalar_MagicConst_Function
    args: list[Node] | list[Stmt]


@define
class Expr_New(Expr):
    class_: Expr | Name | Name_FullyQualified | Stmt_Class
    args: list[Node] | list[Stmt]


@define
class Expr_NullsafeMethodCall(Expr):
    var: Expr
    name: Identifier
    args: list[Node] | list[Stmt]


@define
class Expr_NullsafePropertyFetch(Expr):
    var: Expr
    name: Identifier


@define
class Expr_PostDec(Expr):
    var: Expr


@define
class Expr_PostInc(Expr):
    var: Expr


@define
class Expr_PreDec(Expr):
    var: Expr


@define
class Expr_PreInc(Expr):
    var: Expr


@define
class Expr_Print(Expr):
    expr: Scalar_String


@define
class Expr_PropertyFetch(Expr):
    var: Expr
    name: Expr | Identifier | Scalar_String


@define
class Expr_ShellExec(Expr):
    parts: list[Node]


@define
class Expr_StaticCall(Expr):
    class_: Expr | Name | Name_FullyQualified
    name: Expr | Identifier | Scalar_MagicConst_Class
    args: list[Node] | list[Stmt]


@define
class Expr_StaticPropertyFetch(Expr):
    class_: Expr | Name | Scalar_String
    name: Expr | VarLikeIdentifier


@define
class Expr_Ternary(Expr):
    if_: Expr | None | Scalar_Encapsed | Scalar_LNumber | Scalar_String
    cond: Expr
    else_: Expr | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_String


@define
class Expr_Throw(Expr):
    expr: Expr


@define
class Expr_UnaryMinus(Expr):
    expr: Expr | Scalar_DNumber | Scalar_LNumber


@define
class Expr_UnaryPlus(Expr):
    expr: Expr | Scalar_LNumber


@define
class Expr_Variable(Expr):
    name: Expr | str


@define
class Expr_Yield(Expr):
    key: Expr | None | Scalar_String
    value: Expr | Scalar_LNumber | Scalar_String


@define
class Expr_YieldFrom(Expr):
    expr: Expr


@define
class Identifier(Node):
    name: str


@define
class MatchArm(Node):
    conds: None | list[Expr] | list[Scalar]
    body: Expr | Scalar_LNumber | Scalar_String


@define
class Name(Node):
    parts: list[Any]


@define
class Name_FullyQualified(Node):
    parts: list[Any]


@define
class NullableType(Node):
    type: Identifier | Name | Name_FullyQualified


@define
class Param(Node):
    flags: int
    attrGroups: list[Stmt]
    default: Expr | None | Scalar_DNumber | Scalar_LNumber | Scalar_String
    byRef: int
    variadic: int
    var: Expr
    type: Identifier | Name | Name_FullyQualified | None | NullableType | UnionType


@define
class Scalar_DNumber(Scalar):
    value: float | int


@define
class Scalar_Encapsed(Scalar):
    parts: list[Expr] | list[Node]


@define
class Scalar_EncapsedStringPart(Scalar):
    value: str


@define
class Scalar_LNumber(Scalar):
    value: int


@define
class Scalar_MagicConst_Class(Scalar):
    pass


@define
class Scalar_MagicConst_Dir(Scalar):
    pass


@define
class Scalar_MagicConst_File(Scalar):
    pass


@define
class Scalar_MagicConst_Function(Scalar):
    pass


@define
class Scalar_MagicConst_Line(Scalar):
    pass


@define
class Scalar_MagicConst_Method(Scalar):
    pass


@define
class Scalar_MagicConst_Namespace(Scalar):
    pass


@define
class Scalar_String(Scalar):
    value: str


@define
class Stmt_Break(Stmt):
    num: None | Scalar_LNumber


@define
class Stmt_Case(Stmt):
    cond: Expr | None | Scalar_LNumber | Scalar_String
    stmts: list[Stmt]


@define
class Stmt_Catch(Stmt):
    var: Expr
    types: list[Node]
    stmts: list[Stmt]


@define
class Stmt_Class(Stmt):
    attrGroups: list[Stmt]
    flags: int
    extends: Name | Name_FullyQualified | None
    implements: list[Node] | list[Stmt]
    namespacedName: None
    stmts: list[Stmt]
    name: Identifier | None


@define
class Stmt_ClassConst(Stmt):
    flags: int
    attrGroups: list[Stmt]
    consts: list[Node]


@define
class Stmt_ClassMethod(Stmt):
    flags: int
    attrGroups: list[Node] | list[Stmt]
    byRef: int
    returnType: Identifier | Name | Name_FullyQualified | None | NullableType | UnionType
    stmts: None | list[Stmt]
    params: list[Node] | list[Stmt]
    name: Identifier


@define
class Stmt_Const(Stmt):
    consts: list[Node]


@define
class Stmt_Continue(Stmt):
    num: None | Scalar_LNumber


@define
class Stmt_Declare(Stmt):
    stmts: None
    declares: list[Stmt]


@define
class Stmt_DeclareDeclare(Stmt):
    key: Identifier
    value: Scalar_LNumber


@define
class Stmt_Do(Stmt):
    stmts: list[Stmt]
    cond: Expr | Scalar_LNumber


@define
class Stmt_Echo(Stmt):
    exprs: list[Expr] | list[Node] | list[Scalar]


@define
class Stmt_Else(Stmt):
    stmts: list[Stmt]


@define
class Stmt_ElseIf(Stmt):
    cond: Expr
    stmts: list[Stmt]


@define
class Stmt_Enum(Stmt):
    attrGroups: list[Stmt]
    scalarType: Identifier | None
    implements: list[Stmt]
    namespacedName: None
    stmts: list[Stmt]
    name: Identifier


@define
class Stmt_EnumCase(Stmt):
    expr: None | Scalar_LNumber | Scalar_String
    attrGroups: list[Stmt]
    name: Identifier


@define
class Stmt_Expression(Stmt):
    expr: Expr


@define
class Stmt_Finally(Stmt):
    stmts: list[Stmt]


@define
class Stmt_For(Stmt):
    loop: list[Expr] | list[Stmt]
    init: list[Expr] | list[Stmt]
    cond: list[Expr] | list[Stmt]
    stmts: list[Stmt]


@define
class Stmt_Foreach(Stmt):
    expr: Expr
    valueVar: Expr
    byRef: int
    stmts: list[Stmt]
    keyVar: Expr | None


@define
class Stmt_Function(Stmt):
    attrGroups: list[Stmt]
    byRef: int
    returnType: Identifier | Name | None | NullableType
    namespacedName: None
    stmts: list[Stmt]
    params: list[Node] | list[Stmt]
    name: Identifier


@define
class Stmt_Global(Stmt):
    vars: list[Expr]


@define
class Stmt_Goto(Stmt):
    name: Identifier


@define
class Stmt_GroupUse(Stmt):
    uses: list[Stmt]
    type: int
    prefix: Name


@define
class Stmt_If(Stmt):
    elseifs: list[Stmt]
    cond: Expr | Scalar_LNumber
    stmts: list[Stmt]
    else_: None | Stmt_Else


@define
class Stmt_InlineHTML(Stmt):
    value: str


@define
class Stmt_Interface(Stmt):
    attrGroups: list[Stmt]
    extends: list[Node] | list[Stmt]
    namespacedName: None
    stmts: list[Stmt]
    name: Identifier


@define
class Stmt_Label(Stmt):
    name: Identifier


@define
class Stmt_Namespace(Stmt):
    stmts: list[Stmt]
    name: Name | None


@define
class Stmt_Nop(Stmt):
    pass


@define
class Stmt_Property(Stmt):
    flags: int
    attrGroups: list[Stmt]
    type: Identifier | Name | Name_FullyQualified | None | NullableType | UnionType
    props: list[Stmt]


@define
class Stmt_PropertyProperty(Stmt):
    default: Expr | None | Scalar_LNumber | Scalar_String
    name: VarLikeIdentifier


@define
class Stmt_Return(Stmt):
    expr: Expr | None | Scalar_DNumber | Scalar_Encapsed | Scalar_LNumber | Scalar_MagicConst_Dir | Scalar_String


@define
class Stmt_Static(Stmt):
    vars: list[Stmt]


@define
class Stmt_StaticVar(Stmt):
    var: Expr
    default: Expr | None | Scalar_LNumber | Scalar_String


@define
class Stmt_Switch(Stmt):
    cases: list[Stmt]
    cond: Expr


@define
class Stmt_Throw(Stmt):
    expr: Expr


@define
class Stmt_Trait(Stmt):
    attrGroups: list[Stmt]
    namespacedName: None
    stmts: list[Stmt]
    name: Identifier


@define
class Stmt_TraitUse(Stmt):
    adaptations: list[Stmt]
    traits: list[Node]


@define
class Stmt_TraitUseAdaptation_Alias(Stmt):
    newModifier: None | int
    newName: Identifier
    method: Identifier
    trait: Name | None


@define
class Stmt_TryCatch(Stmt):
    finally_: None | Stmt_Finally
    stmts: list[Stmt]
    catches: list[Stmt]


@define
class Stmt_Unset(Stmt):
    vars: list[Expr]


@define
class Stmt_Use(Stmt):
    uses: list[Stmt]
    type: int


@define
class Stmt_UseUse(Stmt):
    alias: Identifier | None
    type: int
    name: Name


@define
class Stmt_While(Stmt):
    cond: Expr | Scalar_LNumber
    stmts: list[Stmt]


@define
class UnionType(Node):
    types: list[Node]


@define
class VarLikeIdentifier(Node):
    name: str


