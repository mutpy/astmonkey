import ast
import re
from contextlib import contextmanager

import pydot

from astmonkey import utils
from astmonkey.transformers import ParentChildNodeTransformer
from astmonkey.utils import CommaWriter, check_version


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
                value_label = self._dot_node_value_label(value)
                if value_label:
                    fields_labels.append('{0}={1}'.format(field, value_label))
        return 'ast.{0}({1})'.format(node.__class__.__name__, ', '.join(fields_labels))

    def _dot_node_value_label(self, value):
        if not isinstance(value, ast.AST):
            return repr(value)
        elif len(value.parents) > 1:
            return self._dot_node_label(value)
        return None

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


"""
Source generator node visitor from Python AST was originaly written by Armin Ronacher (2008), license BSD.
"""

BOOLOP_SYMBOLS = {
    ast.And: 'and',
    ast.Or: 'or'
}

BINOP_SYMBOLS = {
    ast.Add: '+',
    ast.Sub: '-',
    ast.Mult: '*',
    ast.Div: '/',
    ast.FloorDiv: '//',
    ast.Mod: '%',
    ast.LShift: '<<',
    ast.RShift: '>>',
    ast.BitOr: '|',
    ast.BitAnd: '&',
    ast.BitXor: '^',
    ast.Pow: '**'
}

if check_version(from_inclusive=(3, 5)):
    BINOP_SYMBOLS[ast.MatMult] = '@'

CMPOP_SYMBOLS = {
    ast.Eq: '==',
    ast.Gt: '>',
    ast.GtE: '>=',
    ast.In: 'in',
    ast.Is: 'is',
    ast.IsNot: 'is not',
    ast.Lt: '<',
    ast.LtE: '<=',
    ast.NotEq: '!=',
    ast.NotIn: 'not in'
}

UNARYOP_SYMBOLS = {
    ast.Invert: '~',
    ast.Not: 'not',
    ast.UAdd: '+',
    ast.USub: '-'
}

ALL_SYMBOLS = {}
ALL_SYMBOLS.update(BOOLOP_SYMBOLS)
ALL_SYMBOLS.update(BINOP_SYMBOLS)
ALL_SYMBOLS.update(CMPOP_SYMBOLS)
ALL_SYMBOLS.update(UNARYOP_SYMBOLS)


def to_source(node, indent_with=' ' * 4):
    """This function can convert a node tree back into python sourcecode.
    This is useful for debugging purposes, especially if you're dealing with
    custom asts not generated by python itself.

    It could be that the sourcecode is evaluable when the AST itself is not
    compilable / evaluable.  The reason for this is that the AST contains some
    more data than regular sourcecode does, which is dropped during
    conversion.

    Each level of indentation is replaced with `indent_with`.  Per default this
    parameter is equal to four spaces as suggested by PEP 8, but it might be
    adjusted to match the application's styleguide.
    """
    ParentChildNodeTransformer().visit(node)
    FixLinenoNodeVisitor().visit(node)
    generator = SourceGeneratorNodeVisitor(indent_with)
    generator.visit(node)

    return ''.join(generator.result)


class FixLinenoNodeVisitor(ast.NodeVisitor):
    """A helper node visitor for the SourceGeneratorNodeVisitor.

    Attempts to correct implausible line numbers. An example would be:

    1: while a:
    2:   pass
    3: for a:
    2:   pass

    This would be corrected to:

    1: while a:
    2:   pass
    3: for a:
    4:   pass
    """

    def __init__(self):
        self.min_lineno = 0

    def generic_visit(self, node):
        if hasattr(node, 'lineno'):
            self._fix_lineno(node)
        if hasattr(node, 'body') and isinstance(node.body, list):
            self._process_body(node)

    def _fix_lineno(self, node):
        if node.lineno < self.min_lineno:
            node.lineno = self.min_lineno
        else:
            self.min_lineno = node.lineno

    def _process_body(self, node):
        for body_node in node.body:
            self.min_lineno += 1
            self.visit(body_node)


class BaseSourceGeneratorNodeVisitor(ast.NodeVisitor):
    """This visitor is able to transform a well formed syntax tree into python
    sourcecode.  For more details have a look at the docstring of the
    `node_to_source` function.
    """

    def __init__(self, indent_with):
        self.result = []
        self.indent_with = indent_with
        self.indentation = 0

    @classmethod
    def _is_node_args_valid(cls, node, arg_name):
        return hasattr(node, arg_name) and getattr(node, arg_name) is not None

    def _get_current_line_no(self):
        lines = len("".join(self.result).split('\n')) if self.result else 0
        return lines

    @classmethod
    def _get_actual_lineno(cls, node):
        if isinstance(node, (ast.Expr, ast.Str)) and node.col_offset == -1:
            str_content = cls._get_string_content(node)
            node_lineno = node.lineno - str_content.count('\n')
        else:
            node_lineno = node.lineno
        return node_lineno

    @staticmethod
    def _get_string_content(node):
        # node is a multi line string and the line number is actually the last line
        if isinstance(node, ast.Expr):
            str_content = node.value.s
        else:
            str_content = node.s
        if type(str_content) == bytes:
            str_content = str_content.decode("utf-8")
        return str_content

    def _newline_needed(self, node):
        lines = self._get_current_line_no()
        node_lineno = self._get_actual_lineno(node)
        line_diff = node_lineno - lines
        return line_diff > 0

    @contextmanager
    def indent(self, count=1):
        self.indentation += count
        yield
        self.indentation -= count

    @contextmanager
    def inside(self, pre, post, cond=True):
        if cond:
            self.write(pre)
        yield
        if cond:
            self.write(post)

    def write(self, x):
        self.result.append(x)

    def correct_line_number(self, node, within_statement=True, use_line_continuation=True):
        if not node or not self._is_node_args_valid(node, 'lineno'):
            return
        if within_statement:
            indent = 1
        else:
            indent = 0
        with self.indent(indent):
            self.add_missing_lines(node, within_statement, use_line_continuation)

    def add_missing_lines(self, node, within_statement, use_line_continuation):
        while self._newline_needed(node):
            self.add_line(within_statement, use_line_continuation)

    def add_line(self, within_statement, use_line_continuation):
        if within_statement and use_line_continuation:
            self.result.append('\\')
        self.write_newline()

    def write_newline(self):
        if self.result:
            self.result.append('\n')
        self.result.append(self.indent_with * self.indentation)

    def body(self, statements, indent=1):
        if statements:
            with self.indent(indent):
                for stmt in statements:
                    self.correct_line_number(stmt, within_statement=False)
                    self.visit(stmt)

    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            self.or_else(node)

    def keyword_and_body(self, keyword, body):
        if self._newline_needed(body[0]):
            self.write_newline()
        self.write(keyword)
        self.body(body)

    def or_else(self, node):
        self.keyword_and_body('else:', node.orelse)

    def docstring(self, node):
        s = repr(node.s)
        s = re.sub(r'(?<!\\)\\n', '\n', s)
        s = re.sub(r'(?<!\\)\\t', '\t', s)
        self.write('%s%s%s' % (s[0] * 2, s, s[0] * 2))

    def signature(self, node, add_space=False):
        write_comma = CommaWriter(self.write, add_space_at_beginning=add_space)
        padding = [None] * (len(node.args) - len(node.defaults))

        for arg, default in zip(node.args, padding + node.defaults):
            self.signature_arg(arg, default, write_comma)

        self.signature_spec_arg(node, 'vararg', write_comma, prefix='*')
        self.signature_kwonlyargs(node, write_comma)
        self.signature_spec_arg(node, 'kwarg', write_comma, prefix='**')

    def signature_arg(self, arg, default, write_comma, prefix=''):
        write_comma()
        self.write(prefix)
        self.visit(arg)

        if self._is_node_args_valid(arg, 'annotation'):
            self.write(': ')
            self.visit(arg.annotation)
            if default is not None:
                self.write(' = ')
                self.visit(default)
        elif default is not None:
            self.write('=')
            self.visit(default)

    def signature_kwonlyargs(self, node, write_comma):
        if not self._is_node_args_valid(node, 'kwonlyargs') or len(node.kwonlyargs) == 0:
            return

        if not node.vararg:
            write_comma()
            self.write('*')

        for arg, default in zip(node.kwonlyargs, node.kw_defaults):
            self.signature_arg(arg, default, write_comma)

    def signature_spec_arg(self, node, var, write_comma, prefix):
        arg = getattr(node, var)
        if arg:
            if hasattr(node, var + 'annotation'):
                arg = ast.arg(arg, getattr(node, var + 'annotation'))
            self.signature_arg(arg, None, write_comma, prefix)

    def decorators(self, node):
        if node.decorator_list:
            for decorator in node.decorator_list:
                self.write('@')
                self.visit(decorator)
                self.write_newline()

    def visit(self, node):
        self.correct_line_number(node)
        return super(BaseSourceGeneratorNodeVisitor, self).visit(node)

    # Statements

    def visit_Module(self, node):
        self.body(node.body, indent=0)

    def visit_Assign(self, node):

        for idx, target in enumerate(node.targets):
            if idx:
                self.write(' = ')
            self.visit(target)
        self.write(' = ')
        self.visit(node.value)

    def visit_AugAssign(self, node):

        self.visit(node.target)
        self.write(' ' + BINOP_SYMBOLS[type(node.op)] + '= ')
        self.visit(node.value)

    def visit_ImportFrom(self, node):

        imports = []
        for alias in node.names:
            name = alias.name
            if alias.asname:
                name += ' as ' + alias.asname
            imports.append(name)
        self.write('from {0}{1} import {2}'.format('.' * node.level, node.module or '', ', '.join(imports)))

    def visit_Import(self, node):
        write_comma = CommaWriter(self.write)
        self.write('import ')
        for item in node.names:
            write_comma()
            self.visit(item)

    def visit_Expr(self, node):
        self.correct_line_number(node)
        if isinstance(node.value, ast.Str):
            self.docstring(node.value)
        else:
            self.generic_visit(node)

    def visit_keyword(self, node):
        if self._is_node_args_valid(node, 'arg'):
            self.write(node.arg + '=')
        else:
            self.write('**')
        self.visit(node.value)

    def visit_FunctionDef(self, node):
        self.function_definition(node)

    def function_definition(self, node, prefixes=()):
        self.decorators(node)

        self._prefixes(prefixes)
        self.write('def %s(' % node.name)
        self.signature(node.args)
        self.write('):')
        self.body(node.body)

    def _prefixes(self, prefixes):
        self.write(' '.join(prefixes))
        if prefixes:
            self.write(' ')

    def visit_ClassDef(self, node):
        have_args = []

        def paren_or_comma():
            if have_args:
                self.write(', ')
            else:
                have_args.append(True)
                self.write('(')

        self.decorators(node)

        self.write('class %s' % node.name)
        for base in node.bases:
            paren_or_comma()
            self.visit(base)
        self.write(have_args and '):' or ':')
        self.body(node.body)

    def visit_If(self, node):
        self.if_elif(node)

    def if_elif(self, node, use_elif=False):
        self.correct_line_number(node, within_statement=False)
        if use_elif:
            self.write('elif ')
        else:
            self.write('if ')
        self.visit(node.test)
        self.write(':')
        self.body(node.body)
        if node.orelse:
            self.if_or_else(node)

    def if_or_else(self, node):
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            self.if_elif(node.orelse[0], use_elif=True)
        else:
            self.or_else(node)

    def visit_For(self, node):
        self.for_loop(node)

    def for_loop(self, node, prefixes=()):
        self._prefixes(prefixes)
        self.write('for ')
        self.visit(node.target)
        self.write(' in ')
        self.visit(node.iter)
        self.write(':')
        self.body_or_else(node)

    def visit_While(self, node):
        self.write('while ')
        self.visit(node.test)
        self.write(':')
        self.body_or_else(node)

    def visit_Pass(self, node):
        self.write('pass')

    def visit_Print(self, node):
        self.correct_line_number(node)
        self.write('print ')
        want_comma = False
        if node.dest is not None:
            self.write('>> ')
            self.visit(node.dest)
            want_comma = True
        for value in node.values:
            if want_comma:
                self.write(', ')
            self.visit(value)
            want_comma = True
        if not node.nl:
            self.write(',')

    def visit_Delete(self, node):
        self.write('del ')
        for target in node.targets:
            self.visit(target)
            if target is not node.targets[-1]:
                self.write(', ')

    def visit_Global(self, node):
        self.write('global ' + ', '.join(node.names))

    def visit_Nonlocal(self, node):
        self.write('nonlocal ' + ', '.join(node.names))

    def visit_Return(self, node):

        self.write('return')
        if node.value:
            self.write(' ')
            self.visit(node.value)

    def visit_Break(self, node):
        self.write('break')

    def visit_Continue(self, node):
        self.write('continue')

    def visit_Raise(self, node):

        self.write('raise')
        if self._is_node_args_valid(node, 'exc'):
            self.raise_exc(node)
        elif self._is_node_args_valid(node, 'type'):
            self.raise_type(node)

    def raise_type(self, node):
        self.write(' ')
        self.visit(node.type)
        if node.inst is not None:
            self.write(', ')
            self.visit(node.inst)
        if node.tback is not None:
            self.write(', ')
            self.visit(node.tback)

    def raise_exc(self, node):
        self.write(' ')
        self.visit(node.exc)
        if node.cause is not None:
            self.write(' from ')
            self.visit(node.cause)

    # Expressions

    def visit_Attribute(self, node):
        self.visit(node.value)
        self.write('.' + node.attr)

    def visit_Call(self, node):
        self.visit(node.func)
        with self.inside('(', ')'):
            starargs = getattr(node, 'starargs', None)
            kwargs = getattr(node, 'kwargs', None)
            if starargs:
                starargs = [starargs]
            else:
                starargs = []
            if kwargs:
                kwargs = [kwargs]
            else:
                kwargs = []
            self.call_signature(node.args, node.keywords, starargs, kwargs)

    def call_signature(self, args, keywords, starargs, kwargs):
        write_comma = CommaWriter(self.write)
        self.call_signature_part(args, self.call_arg, write_comma)
        self.call_signature_part(keywords, self.call_keyword, write_comma)
        self.call_signature_part(starargs, self.call_starargs, write_comma)
        self.call_signature_part(kwargs, self.call_kwarg, write_comma)

    def call_signature_part(self, args, arg_processor, write_comma):
        for arg in args:
            write_comma()
            self.correct_line_number(arg, use_line_continuation=False)
            arg_processor(arg)

    def call_kwarg(self, kwarg):
        self.write('**')
        self.visit(kwarg)

    def call_starargs(self, stararg):
        self.write('*')
        self.visit(stararg)

    def call_keyword(self, keyword):
        self.visit(keyword)

    def call_arg(self, arg):
        self.visit(arg)

    def visit_Name(self, node):
        self.write(node.id)

    def visit_str(self, node):
        self.write(node)

    def visit_Str(self, node):
        self.write(repr(node.s))

    def visit_Bytes(self, node):
        self.write(repr(node.s))

    def visit_Num(self, node):
        value = node.n.imag if isinstance(node.n, complex) else node.n

        with self.inside('(', ')', cond=(value < 0)):
            self.write(repr(node.n))

    def visit_Tuple(self, node):
        with self.inside('(', ')'):
            idx = -1
            for idx, item in enumerate(node.elts):
                if idx:
                    self.write(', ')
                self.visit(item)
            if not idx:
                self.write(',')

    def sequence_visit(left, right):  # @NoSelf
        def visit(self, node):
            with self.inside(left, right):
                for idx, item in enumerate(node.elts):
                    if idx:
                        self.write(', ')
                    self.visit(item)

        return visit

    visit_List = sequence_visit('[', ']')
    visit_Set = sequence_visit('{', '}')
    del sequence_visit

    def visit_Dict(self, node):
        with self.inside('{', '}'):
            for idx, (key, value) in enumerate(zip(node.keys, node.values)):
                if idx:
                    self.write(', ')
                if key:
                    self.visit(key)
                    self.write(': ')
                else:
                    self.write('**')
                self.visit(value)

    def visit_BinOp(self, node):
        with self.inside('(', ')', cond=isinstance(node.parent, (ast.BinOp, ast.Attribute))):
            self.visit(node.left)
            self.write(' %s ' % BINOP_SYMBOLS[type(node.op)])
            self.visit(node.right)

    def visit_BoolOp(self, node):
        with self.inside('(', ')'):
            for idx, value in enumerate(node.values):
                if idx:
                    self.write(' %s ' % BOOLOP_SYMBOLS[type(node.op)])
                self.visit(value)

    def visit_Compare(self, node):
        with self.inside('(', ')', cond=(isinstance(node.parent, ast.Compare))):
            self.visit(node.left)
            for op, right in zip(node.ops, node.comparators):
                self.write(' %s ' % CMPOP_SYMBOLS[type(op)])
                self.visit(right)

    def visit_UnaryOp(self, node):
        with self.inside('(', ')', cond=isinstance(node.parent, (ast.BinOp, ast.UnaryOp))):
            op = UNARYOP_SYMBOLS[type(node.op)]
            self.write(op)
            if op == 'not':
                self.write(' ')

            with self.inside('(', ')', cond=(not isinstance(node.operand, (ast.Name, ast.Num))
                                             and not self._is_named_constant(node.operand))):
                self.visit(node.operand)

    def visit_Subscript(self, node):
        self.visit(node.value)
        with self.inside('[', ']'):
            if isinstance(node.slice, ast.Tuple):
                idx = -1
                for idx, item in enumerate(node.slice.elts):
                    if idx:
                        self.write(', ')
                    self.visit(item)
                if not idx:
                    self.write(',')
            else:
                self.visit(node.slice)

    def visit_Slice(self, node):
        self.slice_lower(node)
        self.write(':')
        self.slice_upper(node)
        self.slice_step(node)

    def slice_step(self, node):
        if node.step is not None:
            self.write(':')
            if not (isinstance(node.step, ast.Name) and node.step.id == 'None'):
                self.visit(node.step)

    def slice_upper(self, node):
        if node.upper is not None:
            self.visit(node.upper)

    def slice_lower(self, node):
        if node.lower is not None:
            self.visit(node.lower)

    def visit_ExtSlice(self, node):
        for idx, item in enumerate(node.dims):
            if idx:
                self.write(',')
            self.visit(item)

    def visit_Yield(self, node):
        self.write('yield')
        if node.value:
            self.write(' ')
            self.visit(node.value)

    def visit_Lambda(self, node):
        with self.inside('(', ')', cond=isinstance(node.parent, ast.Call)):
            self.write('lambda')
            self.signature(node.args, add_space=True)
            self.write(': ')
            with self.inside('(', ')'):
                self.visit(node.body)

    def visit_Ellipsis(self, node):
        self.write('...')

    def generator_visit(left, right):  # @NoSelf
        def visit(self, node):
            self.write(left)
            self.visit(node.elt)
            for comprehension in node.generators:
                self.visit(comprehension)
            self.write(right)

        return visit

    visit_ListComp = generator_visit('[', ']')
    visit_GeneratorExp = generator_visit('(', ')')
    visit_SetComp = generator_visit('{', '}')
    del generator_visit

    def visit_DictComp(self, node):
        with self.inside('{', '}'):
            self.visit(node.key)
            self.write(': ')
            self.visit(node.value)
            for comprehension in node.generators:
                self.visit(comprehension)

    def visit_IfExp(self, node):
        with self.inside('(', ')', cond=isinstance(node.parent, ast.BinOp)):
            self.visit(node.body)
            self.write(' if ')
            self.visit(node.test)
            self.keyword_and_body(' else ', [node.orelse])

    def visit_Starred(self, node):
        self.write('*')
        self.visit(node.value)

    def visit_Repr(self, node):
        with self.inside('`', '`'):
            self.visit(node.value)

    # Helper Nodes
    def visit_alias(self, node):
        self.write(node.name)
        if node.asname is not None:
            self.write(' as ' + node.asname)

    def visit_comprehension(self, node):
        if getattr(node, 'is_async', 0):
            self.write(' async')
        self.write(' for ')
        self.visit(node.target)
        self.write(' in ')
        self.visit(node.iter)
        if node.ifs:
            for if_ in node.ifs:
                self.write(' if ')
                self.visit(if_)

    def visit_ExceptHandler(self, node):
        self.write('except')
        if node.type is not None:
            self.write(' ')
            self.visit(node.type)
            if node.name is not None:
                self.write(' as ')
                self.visit(node.name)
        self.write(':')
        self.body(node.body)

    def visit_arg(self, node):
        self.write(node.arg)

    def visit_Assert(self, node):
        self.write('assert ')
        self.visit(node.test)
        if node.msg:
            self.write(', ')
            self.visit(node.msg)

    def visit_TryExcept(self, node):
        self.write('try:')
        self.body(node.body)
        if node.handlers:
            self.try_handlers(node)
        if node.orelse:
            self.or_else(node)

    def try_handlers(self, node):
        for handler in node.handlers:
            self.correct_line_number(handler, within_statement=False)
            self.visit(handler)

    def visit_TryFinally(self, node):
        self.write('try:')
        self.body(node.body)
        self.final_body(node)

    def final_body(self, node):
        self.keyword_and_body('finally:', node.finalbody)

    def visit_With(self, node):
        self.with_body(node)

    def with_body(self, node, prefixes=[]):
        self._prefixes(prefixes)
        self.write('with ')
        self.visit(node.context_expr)
        if node.optional_vars is not None:
            self.write(' as ')
            self.visit(node.optional_vars)
        self.write(':')
        self.body(node.body)

    @staticmethod
    def _is_named_constant(node):
        return isinstance(node, ast.Expr) and hasattr(node, 'value') and isinstance(node.value, ast.Name)


class SourceGeneratorNodeVisitorPython26(BaseSourceGeneratorNodeVisitor):
    __python_version__ = (2, 6)


class SourceGeneratorNodeVisitorPython27(SourceGeneratorNodeVisitorPython26):
    __python_version__ = (2, 7)


class SourceGeneratorNodeVisitorPython30(SourceGeneratorNodeVisitorPython27):
    __python_version__ = (3, 0)

    def visit_ClassDef(self, node):
        have_args = []

        def paren_or_comma():
            if have_args:
                self.write(', ')
            else:
                have_args.append(True)
                self.write('(')

        self.decorators(node)
        self.correct_line_number(node)
        self.write('class %s' % node.name)
        for base in node.bases:
            paren_or_comma()
            self.visit(base)
        if self._is_node_args_valid(node, 'keywords'):
            for keyword in node.keywords:
                paren_or_comma()
                self.visit(keyword)
        self.write(have_args and '):' or ':')
        self.body(node.body)

    def visit_FunctionDef(self, node):
        self.decorators(node)

        self.write('def %s(' % node.name)
        self.signature(node.args)
        self.write(')')
        if self._is_node_args_valid(node, 'returns'):
            self.write(' -> ')
            self.visit(node.returns)
        self.write(':')
        self.body(node.body)


class SourceGeneratorNodeVisitorPython31(SourceGeneratorNodeVisitorPython30):
    __python_version__ = (3, 1)


class SourceGeneratorNodeVisitorPython32(SourceGeneratorNodeVisitorPython31):
    __python_version__ = (3, 2)


class SourceGeneratorNodeVisitorPython33(SourceGeneratorNodeVisitorPython32):
    __python_version__ = (3, 3)

    def visit_Try(self, node):
        self.write('try:')
        self.body(node.body)
        if node.handlers:
            self.try_handlers(node)
        if node.orelse:
            self.or_else(node)
        if node.finalbody:
            self.final_body(node)

    def with_body(self, node, prefixes=[]):
        self._prefixes(prefixes)
        self.write('with ')
        for with_item in node.items:
            self.visit(with_item.context_expr)
            if with_item.optional_vars is not None:
                self.write(' as ')
                self.visit(with_item.optional_vars)
            if with_item != node.items[-1]:
                self.write(', ')
        self.write(':')
        self.body(node.body)

    def visit_YieldFrom(self, node):
        self.write('yield from ')
        self.visit(node.value)


class SourceGeneratorNodeVisitorPython34(SourceGeneratorNodeVisitorPython33):
    __python_version__ = (3, 4)

    def visit_NameConstant(self, node):
        self.write(str(node.value))

    def visit_Name(self, node):
        if isinstance(node.id, ast.arg):
            self.write(node.id.arg)
        else:
            self.write(node.id)

    @staticmethod
    def _is_named_constant(node):
        return isinstance(node, ast.NameConstant)


class SourceGeneratorNodeVisitorPython35(SourceGeneratorNodeVisitorPython34):
    __python_version__ = (3, 5)

    def visit_AsyncFunctionDef(self, node):
        self.function_definition(node, prefixes=['async'])

    def visit_AsyncFor(self, node):
        self.for_loop(node, prefixes=['async'])

    def visit_AsyncWith(self, node):
        self.with_body(node, prefixes=['async'])

    def visit_Await(self, node):
        self.write('await ')
        if self._is_node_args_valid(node, 'value'):
            self.visit(node.value)

    def visit_Call(self, node):
        self.visit(node.func)
        with self.inside('(', ')'):
            args, starargs = self._separate_args_and_starargs(node)
            keywords, kwargs = self._separate_keywords_and_kwargs(node)
            self.call_signature(args, keywords, starargs, kwargs)

    @staticmethod
    def _separate_keywords_and_kwargs(node):
        keywords = []
        kwargs = []
        for keyword in node.keywords:
            if keyword.arg:
                keywords.append(keyword)
            else:
                kwargs.append(keyword)
        return keywords, kwargs

    @staticmethod
    def _separate_args_and_starargs(node):
        args = []
        starargs = []
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                starargs.append(arg)
            else:
                args.append(arg)
        return args, starargs

    def call_starargs(self, stararg):
        self.visit(stararg)

    def call_kwarg(self, kwarg):
        self.visit(kwarg)


class SourceGeneratorNodeVisitorPython36(SourceGeneratorNodeVisitorPython35):
    __python_version__ = (3, 6)

    def visit_JoinedStr(self, node):
        if self._is_node_args_valid(node, 'values'):
            with self.inside('f\'', '\''):
                for item in node.values:
                    if isinstance(item, ast.Str):
                        self.write(item.s.lstrip('\'').rstrip('\'').replace("'", "\\'"))
                    else:
                        self.visit(item)

    def visit_FormattedValue(self, node):
        if self._is_node_args_valid(node, 'value'):
            self.add_missing_lines(node.value, True, True)
            with self.inside('{', '}'):
                self.visit(node.value)
                if node.conversion != -1:
                    self.write('!%c' % (node.conversion,))

    def visit_AnnAssign(self, node):
        self.visit(node.target)
        self.write(': ')
        self.visit(node.annotation)
        self.write(' = ')
        self.visit(node.value)

class SourceGeneratorNodeVisitorPython38(SourceGeneratorNodeVisitorPython36):
    __python_version__ = (3, 8)

    def visit_Constant(self, node):
        if type(node.value) == str:
            self.write(repr(node.s))
        elif node.value == Ellipsis:
            self.write('...')
        else:
            self.write(str(node.value))

    def visit_NamedExpr(self, node):
        self.visit(node.target)
        self.write(' := ')
        self.visit(node.value)

    def signature(self, node, add_space=False):
        write_comma = CommaWriter(self.write, add_space_at_beginning=add_space)


        defaults = list(node.defaults)

        if node.posonlyargs:
            padding = [None] * (len(node.posonlyargs) - len(node.defaults))
            for arg, default in zip(node.posonlyargs, padding + defaults[:len(node.posonlyargs)]):
                self.signature_arg(arg, default, write_comma)
            self.write(', /')
            defaults = defaults[len(node.posonlyargs):]

        padding = [None] * (len(node.args) - len(node.defaults))
        for arg, default in zip(node.args, padding + defaults):
            self.signature_arg(arg, default, write_comma)

        self.signature_spec_arg(node, 'vararg', write_comma, prefix='*')
        self.signature_kwonlyargs(node, write_comma)
        self.signature_spec_arg(node, 'kwarg', write_comma, prefix='**')

    @classmethod
    def _get_actual_lineno(cls, node):
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            return node.decorator_list[0].lineno
        else:
            return SourceGeneratorNodeVisitorPython36._get_actual_lineno(node)


SourceGeneratorNodeVisitor = utils.get_by_python_version([
    SourceGeneratorNodeVisitorPython26,
    SourceGeneratorNodeVisitorPython27,
    SourceGeneratorNodeVisitorPython30,
    SourceGeneratorNodeVisitorPython31,
    SourceGeneratorNodeVisitorPython32,
    SourceGeneratorNodeVisitorPython33,
    SourceGeneratorNodeVisitorPython34,
    SourceGeneratorNodeVisitorPython35,
    SourceGeneratorNodeVisitorPython36,
    SourceGeneratorNodeVisitorPython38
])
