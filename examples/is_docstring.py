import ast
from astmonkey import utils, transformers

node = ast.parse('def foo(x):\n\t"""doc"""')
node = transformers.ParentChildNodeTransformer().visit(node)

docstring_node = node.body[0].body[0].value
assert(not utils.is_docstring(node))
assert(utils.is_docstring(docstring_node))
