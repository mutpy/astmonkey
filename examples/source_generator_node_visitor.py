import ast
from astmonkey import visitors

code = 'x = y + 1'
node = ast.parse(code)
generated_code = visitors.to_source(node)

assert(code == generated_code)
