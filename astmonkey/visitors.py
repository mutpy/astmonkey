import ast
import pydot


class GraphNodeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.graph = pydot.Dot(graph_type='graph')

    def visit(self, node):
        self.graph.add_node(self._dot_node(node))
        if node.parent:
            edge = pydot.Edge(str(node.parent), str(node))
            self.graph.add_edge(edge)
        super(GraphNodeVisitor, self).visit(node)

    def _dot_node(self, node):
        fields_labels = []
        for field in node._fields:
            value = getattr(node, field)
            if not isinstance(value, ast.AST) and not isinstance(value, list):
                fields_labels.append('{0}={1}'.format(field, repr(value)))
        label = 'ast.{0}({1})'.format(node.__class__.__name__, ','.join(fields_labels))
        return pydot.Node(str(node), label=label)

