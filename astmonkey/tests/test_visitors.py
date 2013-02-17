import unittest
import ast
from astmonkey import visitors, transformers


class GraphNodeVisitorTest(unittest.TestCase):

    def test_has_edge(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))
        visitor = visitors.GraphNodeVisitor()

        visitor.visit(node)

        self.assertTrue(visitor.graph.get_edge(str(node), str(node.body[0])))

    def test_does_not_have_edge(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))
        visitor = visitors.GraphNodeVisitor()

        visitor.visit(node)

        self.assertFalse(visitor.graph.get_edge(str(node), str(node.body[0].value)))

    def test_label(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))
        visitor = visitors.GraphNodeVisitor()

        visitor.visit(node)

        self.assertEqual(visitor.graph.get_node(str(node.body[0].value))[0].get_label(), 'ast.Num(n=1)')

