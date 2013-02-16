import ast


class ParentNodeTransformer(ast.NodeTransformer):

    def visit(self, node):
        node.parent = getattr(self, 'parent', None)
        self.parent = node
        result_node = super(ParentNodeTransformer, self).visit(node)
        self.parent = node.parent
        return result_node

