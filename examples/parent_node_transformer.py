import ast
from astmonkey import transformers

node = ast.parse('x = 1')
node = transformers.ParentNodeTransformer().visit(node)

assert(node == node.body[0].parent)
assert(node.body[0].parent_field == 'body')
assert(node.body[0].parent_field_index == 0)
