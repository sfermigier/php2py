import ast as py

from devtools import debug

from php2py.php_ast import (
    Expr_Variable,
    Node,
    Scalar_DNumber,
    Scalar_Encapsed,
    Scalar_EncapsedStringPart,
    Scalar_LNumber,
    Scalar_String,
)

# casts = {
#     "double": "float",
#     "string": "str",
#     "array": "list",
# }


class ScalarTranslator:
    def translate_scalar(self, node: Node):
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

    def translate_encapsed(self, node: Node):
        parts = node.parts
        result = []
        for part in parts:
            match part:
                case Scalar_EncapsedStringPart(value=value):
                    result.append(value)
                case Expr_Variable(name=name):
                    result.append(f"{name}")
                case _:
                    debug(part)
                    raise NotImplementedError()

        return py.Str("".join(result))
