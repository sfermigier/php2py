import json
import shlex
import subprocess
import tempfile
from pathlib import Path

from platformdirs import user_cache_dir

from . import php_ast
from .constants import APP_NAME

PHP_PARSE = "vendor/nikic/php-parser/bin/php-parse"


def install_parser(force: bool = False):
    cache_dir = Path(user_cache_dir(APP_NAME))

    php_parse = cache_dir / PHP_PARSE

    if not force and php_parse.exists():
        return

    Path(cache_dir).mkdir(exist_ok=True)

    etc_dir = Path(__file__).parent / "etc"
    print(etc_dir)
    for file in etc_dir.glob("*"):
        dest = cache_dir / file.name
        print(dest)
        if dest.exists():
            continue
        dest.write_text(file.read_text())

    subprocess.run("composer install", shell=True, cwd=cache_dir)


def parse(source_code: str, php_parse: str | Path = ""):
    if not php_parse:
        php_parse = "vendor/nikic/php-parser/bin/php-parse"
    php_parse = Path(php_parse)
    assert php_parse.exists()

    with tempfile.NamedTemporaryFile("w", suffix=".php", delete=False) as source_file:
        source_file.write(source_code)
        source_file.flush()

        cmd_line = f"{php_parse} -j {source_file.name}"
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
        return [make_ast(subnode) for subnode in json_node]

    if isinstance(json_node, str):
        return None

    if json_node is None:
        return None

    assert isinstance(json_node, dict)
    if "nodeType" not in json_node:
        return None

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
            case {"nodeType": _}:
                args[attr] = make_ast(value)
            case _:
                args[attr] = value

    node = node_class(**args)

    # Hacks
    node._json = json_node
    node._attributes = json_node["attributes"]

    return node
