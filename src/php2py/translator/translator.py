import ast as py
from dataclasses import dataclass

from devtools import debug

from php2py.php_ast import Node

from .stmts import StmtTranslator

# casts = {
#     "double": "float",
#     "string": "str",
#     "array": "list",
# }


@dataclass
class Translator(StmtTranslator):
    in_class: bool = False

    def translate_root(self, root_node):
        return py.Module(body=[self.translate(n) for n in root_node], type_ignores=[])

    def translate(self, node: Node):
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
                    parts = node.get_parts()
                    name = parts[0]
                    return py.Name(name, py.Load())

                if node_type == "Name_FullyQualified":
                    parts = node.get_parts()
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
