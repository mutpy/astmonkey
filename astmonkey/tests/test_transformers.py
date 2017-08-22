import pytest

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import ast

from astmonkey import transformers


class TestParentChildNodeTransformer(object):
    @pytest.fixture
    def transformer(self):
        return transformers.ParentChildNodeTransformer()

    def test_module_node(self, transformer):
        node = ast.parse('')

        transformed_node = transformer.visit(node)

        assert transformed_node.parent is None
        assert transformed_node.children == []

    def test_non_module_node(self, transformer):
        node = ast.parse('x = 1')

        transformed_node = transformer.visit(node)

        assign_node = transformed_node.body[0]
        assert transformed_node == assign_node.parent
        assert assign_node.parent_field == 'body'
        assert assign_node.parent_field_index == 0
        assert transformed_node.children == [assign_node]
        assert len(assign_node.children) == 2

    def test_expr_context_nodes(self, transformer):
        node = ast.parse('x = 1\nx = 2')

        transformer.visit(node)

        ctx_node = node.body[0].targets[0].ctx
        first_name_node = node.body[0].targets[0]
        second_name_node = node.body[1].targets[0]
        assert first_name_node in ctx_node.parents
        assert second_name_node in ctx_node.parents
        assert ctx_node in first_name_node.children
        assert ctx_node in second_name_node.children
