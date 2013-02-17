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


class SourceGeneratorNodeVisitorTest(unittest.TestCase):

    def assert_code_equal(self, code):
        node = ast.parse(code)
        generated = visitors.to_source(node, indent_with='\t')
        self.assertMultiLineEqual(code, generated)

    def test_import(self):
        self.assert_code_equal('import x')

    def test_import_from(self):
        self.assert_code_equal('from x import y as z, q as p')

    def test_assign(self):
        self.assert_code_equal('x = 1')

    def test_aug_assign(self):
        self.assert_code_equal('x += 1')

    def test_function_def(self):
        self.assert_code_equal('def foo(x):\n\tpass')

    def test_class_def(self):
        self.assert_code_equal('class X(A):\n\tpass')

    def test_if(self):
        self.assert_code_equal('if x:\n\tpass\nelif y:\n\tpass\nelse:\n\tpass')

    def test_for(self):
        self.assert_code_equal('for x in y:\n\tpass\nelse:\n\tpass')

    def test_while(self):
        self.assert_code_equal('while x:\n\tpass\nelse:\n\tpass')

    def test_print(self):
        self.assert_code_equal('print x')

    def test_delete(self):
        self.assert_code_equal('del x')

    def test_global(self):
        self.assert_code_equal('global x, y')

    def test_return(self):
        self.assert_code_equal('def foo(x):\n\treturn x')

    def test_break(self):
        self.assert_code_equal('while x:\n\tbreak')

    def test_continue(self):
        self.assert_code_equal('while x:\n\tcontinue')

    def test_raise(self):
        self.assert_code_equal('raise x')

    def test_attribute(self):
        self.assert_code_equal('x.y')

    def test_call(self):
        self.assert_code_equal('x(y, z=1, *args, **kwargs)')

    def test_str(self):
        self.assert_code_equal("'x'")

    def test_num(self):
        self.assert_code_equal('1')

    def test_tuple(self):
        self.assert_code_equal('(1, 2)')

    def test_list(self):
        self.assert_code_equal('[1, 2]')

    def test_set(self):
        self.assert_code_equal('{1, 2}')

    def test_dict(self):
        self.assert_code_equal('{1: 2}')

    def test_bin_op(self):
        self.assert_code_equal('x + y')

    def test_bool_op(self):
        self.assert_code_equal('(x and y)')

    def test_bool_op(self):
        self.assert_code_equal('(x and y)')

    def test_compare(self):
        self.assert_code_equal('x < y')

    def test_unary_op(self):
        self.assert_code_equal('(not x)')

    def test_subscript(self):
        self.assert_code_equal('x[y]')

    def test_slice(self):
        self.assert_code_equal('x[y:z:q]')

    def test_yield(self):
        self.assert_code_equal('def foo(x):\n\tyield x')

    def test_lambda(self):
        self.assert_code_equal('lambda x: x')

    def test_list_comp(self):
        self.assert_code_equal('[x for x in y]')

    def test_generator_exp(self):
        self.assert_code_equal('(x for x in y)')

    def test_set_comp(self):
        self.assert_code_equal('{x for x in y}')

    def test_dict_comp(self):
        self.assert_code_equal('{x: y for x in y}')

    def test_if_exp(self):
        self.assert_code_equal('x if y else z')

    def test_try_except(self):
        self.assert_code_equal('try:\n\tpass\nexcept:\n\tpass')

    def test_try_finally(self):
        self.assert_code_equal('try:\n\tpass\nfinally:\n\tpass')

    def test_with(self):
        self.assert_code_equal('with x as y:\n\tpass')

