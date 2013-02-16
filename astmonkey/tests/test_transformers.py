import unittest
import ast
from astmonkey import transformers


class ParentNodeTransformerTest(unittest.TestCase):

    def test_module_node_parent(self):
        node = ast.parse('')

        transformed_node = transformers.ParentNodeTransformer().visit(node)

        self.assertIsNone(transformed_node.parent)

    def test_non_module_node_parent(self):
        node = ast.parse('x = 1')

        transformed_node = transformers.ParentNodeTransformer().visit(node)

        self.assertEqual(transformed_node, transformed_node.body[0].parent)

