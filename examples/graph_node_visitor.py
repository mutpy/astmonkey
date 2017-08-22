import ast
from astmonkey import visitors, transformers

node = ast.parse('def foo(x):\n\treturn x + 1')
node = transformers.ParentChildNodeTransformer().visit(node)
visitor = visitors.GraphNodeVisitor()
visitor.visit(node)

visitor.graph.write_png('graph.png')
