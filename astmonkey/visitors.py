import ast
import pydot


class GraphNodeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.graph = pydot.Dot(graph_type='graph', **self._dot_graph_kwargs())

    def visit(self, node):
        if len(node.parents) <= 1:
            self.graph.add_node(self._dot_node(node))
        if len(node.parents) == 1:
            self.graph.add_edge(self._dot_edge(node))
        super(GraphNodeVisitor, self).visit(node)

    def _dot_graph_kwargs(self):
        return {}

    def _dot_node(self, node):
        return pydot.Node(str(node), label=self._dot_node_label(node), **self._dot_node_kwargs(node))

    def _dot_node_label(self, node):
        fields_labels = []
        for field, value in ast.iter_fields(node):
            if not isinstance(value, list):
                value_label = None
                if not isinstance(value, ast.AST):
                    value_label = repr(value)
                elif len(value.parents) > 1:
                    value_label = self._dot_node_label(value)
                if value_label:
                    fields_labels.append('{0}={1}'.format(field, value_label))
        return 'ast.{0}({1})'.format(node.__class__.__name__, ', '.join(fields_labels))

    def _dot_node_kwargs(self, node):
        return {
            'shape': 'box',
            'fontname': 'Curier'
        }

    def _dot_edge(self, node):
        return pydot.Edge(str(node.parent), str(node), label=self._dot_edge_label(node), **self._dot_edge_kwargs(node))

    def _dot_edge_label(self, node):
        label = node.parent_field
        if not node.parent_field_index is None:
            label += '[{0}]'.format(node.parent_field_index)
        return label

    def _dot_edge_kwargs(self, node):
        return {
            'fontname': 'Curier'
        }

