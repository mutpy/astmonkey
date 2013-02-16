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
