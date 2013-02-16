import ast


def is_docstring(node):
    if node.parent is None or node.parent.parent is None:
        return False
    def_node = node.parent.parent
    return (
        isinstance(def_node, (ast.FunctionDef, ast.ClassDef, ast.Module)) and def_node.body and
        isinstance(def_node.body[0], ast.Expr) and isinstance(def_node.body[0].value, ast.Str) and
        def_node.body[0].value == node
    )

