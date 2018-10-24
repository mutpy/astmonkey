import ast
import sys


def is_docstring(node):
    if node.parent is None or node.parent.parent is None:
        return False
    def_node = node.parent.parent
    return (
            isinstance(def_node, (ast.FunctionDef, ast.ClassDef, ast.Module)) and def_node.body and
            isinstance(def_node.body[0], ast.Expr) and isinstance(def_node.body[0].value, ast.Str) and
            def_node.body[0].value == node
    )


def get_by_python_version(classes, python_version=sys.version_info):
    result = None
    for cls in classes:
        if cls.__python_version__ <= python_version:
            if not result or cls.__python_version__ > result.__python_version__:
                result = cls
    if not result:
        raise NotImplementedError('astmonkey does not support Python %s.' % sys.version)
    return result


class CommaWriter:

    def __init__(self, write_func, add_space_at_beginning=False):
        self.write_func = write_func
        self.add_space_at_beginning = add_space_at_beginning
        self.not_called_yet = True

    def __call__(self, *args, **kwargs):
        if self.not_called_yet:
            self.not_called_yet = False
            if self.add_space_at_beginning:
                self.write_func(' ')
        else:
            self.write_func(', ')

def check_version(from_inclusive=None, to_exclusive=None):
    if (not from_inclusive or sys.version_info >= from_inclusive) \
            and (not to_exclusive or sys.version_info < to_exclusive):
        return True
    return False
