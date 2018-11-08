import ast


class ParentChildNodeTransformer(object):

    def visit(self, node):
        self._prepare_node(node)
        for field, value in ast.iter_fields(node):
            self._process_field(node, field, value)
        return node

    @staticmethod
    def _prepare_node(node):
        if not hasattr(node, 'parent'):
            node.parent = None
        if not hasattr(node, 'parents'):
            node.parents = []
        if not hasattr(node, 'children'):
            node.children = []

    def _process_field(self, node, field, value):
        if isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, ast.AST):
                    self._process_child(item, node, field, index)
        elif isinstance(value, ast.AST):
            self._process_child(value, node, field)

    def _process_child(self, child, parent, field_name, index=None):
        self.visit(child)
        child.parent = parent
        child.parents.append(parent)
        child.parent_field = field_name
        child.parent_field_index = index
        child.parent.children.append(child)
