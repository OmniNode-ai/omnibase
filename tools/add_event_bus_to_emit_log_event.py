import ast
import os
from pathlib import Path

import astor

SRC_ROOT = Path("src/omnibase")


class LogEventTransformer(ast.NodeTransformer):
    def __init__(self):
        self.changed = False

    def visit_Call(self, node):
        # Only modify emit_log_event calls
        if (isinstance(node.func, ast.Name) and node.func.id == "emit_log_event") or (
            isinstance(node.func, ast.Attribute) and node.func.attr == "emit_log_event"
        ):
            # Check if event_bus is already present
            for kw in node.keywords:
                if kw.arg == "event_bus":
                    return self.generic_visit(node)
            # Add event_bus=self._event_bus
            node.keywords.append(
                ast.keyword(
                    arg="event_bus",
                    value=ast.Attribute(
                        value=ast.Name(id="self", ctx=ast.Load()),
                        attr="_event_bus",
                        ctx=ast.Load(),
                    ),
                )
            )
            self.changed = True
        return self.generic_visit(node)


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except Exception as e:
        print(f"[SKIP] {path}: parse error: {e}")
        return False
    transformer = LogEventTransformer()
    transformer.visit(tree)
    if transformer.changed:
        new_source = astor.to_source(tree)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_source)
        print(f"[UPDATED] {path}")
        return True
    return False


def main():
    updated = 0
    checked = 0
    for pyfile in SRC_ROOT.rglob("*.py"):
        checked += 1
        if process_file(pyfile):
            updated += 1
    print(f"Checked {checked} files. Updated {updated} files.")


if __name__ == "__main__":
    main()
