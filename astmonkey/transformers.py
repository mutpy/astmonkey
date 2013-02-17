import ast


class ParentNodeTransformer(object):

    def visit(self, node):
        if not hasattr(node, 'parent'):
            node.parent = None
            node.parents = []
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, ast.AST):
                        self.visit(item)
                        self._set_parnt_fields(item, node, field, index)
            elif isinstance(value, ast.AST):
                self.visit(value)
                self._set_parnt_fields(value, node, field)
        return node

    def _set_parnt_fields(self, node, parent, field, index=None):
        node.parent = parent
        node.parents.append(parent)
        node.parent_field = field
        node.parent_field_index = index

