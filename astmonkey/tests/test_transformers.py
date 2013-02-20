try:
    import unittest2 as unittest
except ImportError:
    import unittest
import ast
from astmonkey import transformers


class ParentNodeTransformerTest(unittest.TestCase):

    def setUp(self):
        self.transformer = transformers.ParentNodeTransformer()

    def test_module_node_parent(self):
        node = ast.parse('')

        transformed_node = self.transformer.visit(node)

        self.assertIsNone(transformed_node.parent)

    def test_non_module_node_parent(self):
        node = ast.parse('x = 1')

        transformed_node = self.transformer.visit(node)

        assign_node = transformed_node.body[0]
        self.assertEqual(transformed_node, assign_node.parent)
        self.assertEqual(assign_node.parent_field, 'body')
        self.assertEqual(assign_node.parent_field_index, 0)

    def test_expr_context_nodes_parent(self):
        node = ast.parse('x = 1\nx = 2')

        transformed_node = self.transformer.visit(node)

        ctx_node = node.body[0].targets[0].ctx
        first_name_node = node.body[0].targets[0]
        second_name_node = node.body[1].targets[0]
        self.assertIn(first_name_node, ctx_node.parents)
        self.assertIn(second_name_node, ctx_node.parents)

