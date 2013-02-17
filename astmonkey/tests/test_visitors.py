import unittest
import ast
from astmonkey import visitors, transformers


class GraphNodeVisitorTest(unittest.TestCase):

    def setUp(self):
        self.visitor = visitors.GraphNodeVisitor()

    def test_has_edge(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))

        self.visitor.visit(node)

        self.assertTrue(self.visitor.graph.get_edge(str(node), str(node.body[0])))

    def test_does_not_have_edge(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))

        self.visitor.visit(node)

        self.assertFalse(self.visitor.graph.get_edge(str(node), str(node.body[0].value)))

    def test_node_label(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))

        self.visitor.visit(node)

        dot_node = self.visitor.graph.get_node(str(node.body[0].value))[0]
        self.assertEqual(dot_node.get_label(), 'ast.Num(n=1)')

    def test_edge_label(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))

        self.visitor.visit(node)

        dot_edge = self.visitor.graph.get_edge(str(node), str(node.body[0]))[0]
        self.assertEqual(dot_edge.get_label(), 'body[0]')

    def test_multi_parents_node_label(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1\nx = 2'))

        self.visitor.visit(node)

        dot_node = self.visitor.graph.get_node(str(node.body[0].targets[0]))[0]
        self.assertEqual(dot_node.get_label(), "ast.Name(id='x', ctx=ast.Store())")

