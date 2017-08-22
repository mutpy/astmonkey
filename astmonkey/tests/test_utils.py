import ast
import unittest

from astmonkey import utils, transformers


class TestIsDocstring(unittest.TestCase):
    def test_non_docstring_node(self):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse(''))

        assert not utils.is_docstring(node)

    def test_module_docstring_node(self):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse('"""doc"""'))

        assert utils.is_docstring(node.body[0].value)

    def test_function_docstring_node(self):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse('def foo():\n\t"""doc"""'))

        assert utils.is_docstring(node.body[0].body[0].value)

    def test_class_docstring_node(self):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse('class X:\n\t"""doc"""'))

        assert utils.is_docstring(node.body[0].body[0].value)
