import json
import shlex
import subprocess
import tempfile

from . import php_ast


def parse(source_code: str):
    with tempfile.NamedTemporaryFile("w", suffix=".php", delete=False) as source_file:
        source_file.write(source_code)
        source_file.flush()

        cmd_line = f"vendor/nikic/php-parser/bin/php-parse -j {source_file.name}"
        args = shlex.split(cmd_line)
        with subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        ) as p:
            json_ast = json.load(p.stdout)
            result = make_ast(json_ast)

    return result


def make_ast(
    json_node: list | dict | str | int | None,
) -> php_ast.Node | list[php_ast.Node] | None:
    if isinstance(json_node, list):
        node = []
        return [make_ast(subnode) for subnode in json_node]

    if isinstance(json_node, str):
        return

    if json_node is None:
        return

    assert isinstance(json_node, dict)
    if "nodeType" not in json_node:
        return

    node_type = json_node["nodeType"]
    node_class = getattr(php_ast, node_type)
    args = {k: None for k in node_class.__annotations__}

    for attr, value in json_node.items():
        if attr in {"nodeType", "attributes"}:
            continue

        remap_attrs = {
            "if": "if_",
            "else": "else_",
            "class": "class_",
            "finally": "finally_",
        }
        attr = remap_attrs.get(attr, attr)

        match value:
            case [*_]:
                args[attr] = make_ast(value)
            case {"nodeType": _, **rest}:
                args[attr] = make_ast(value)
            case _:
                args[attr] = value

    node = node_class(**args)

    # Hacks
    node._json = json_node
    node._attributes = json_node["attributes"]

    return node
