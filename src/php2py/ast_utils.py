from .php_ast import Node


def print_ast(node: Node, level: int = 0):
    print("  " * level + node.__class__.__name__)
    for attr, value in node.__dict__.items():
        if attr.startswith("_"):
            continue

        if isinstance(value, Node):
            print_ast(value, level + 1)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, Node):
                    print_ast(item, level + 1)
        elif value is not None:
            print("  " * (level + 1) + f"{attr}: {value}")
