import unittest
import ast
from astmonkey import utils, transformers


class IsDocstringTest(unittest.TestCase):

    def test_non_docstring_node(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse(''))

        self.assertFalse(utils.is_docstring(node))

    def test_module_docstring_node(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('"""doc"""'))

        self.assertTrue(utils.is_docstring(node.body[0].value))

    def test_function_docstring_node(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('def foo():\n\t"""doc"""'))

        self.assertTrue(utils.is_docstring(node.body[0].body[0].value))

    def test_class_docstring_node(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('class X:\n\t"""doc"""'))

        self.assertTrue(utils.is_docstring(node.body[0].body[0].value))

