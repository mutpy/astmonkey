# -*- coding: utf-8 -*-
import sys

import pytest

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import ast
from astmonkey import visitors, transformers, utils


class TestGraphNodeVisitor(object):
    @pytest.fixture
    def visitor(self):
        return visitors.GraphNodeVisitor()

    def test_has_edge(self, visitor):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse('x = 1'))

        visitor.visit(node)

        assert visitor.graph.get_edge(str(node), str(node.body[0]))

    def test_does_not_have_edge(self, visitor):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse('x = 1'))

        visitor.visit(node)

        assert not visitor.graph.get_edge(str(node), str(node.body[0].value))

    def test_node_label(self, visitor):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse('x = 1'))

        visitor.visit(node)

        dot_node = visitor.graph.get_node(str(node.body[0].value))[0]
        if sys.version_info >= (3, 8):
            assert dot_node.get_label() == 'ast.Constant(value=1, kind=None)'
        else:
            assert dot_node.get_label() == 'ast.Num(n=1)'

    def test_edge_label(self, visitor):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse('x = 1'))

        visitor.visit(node)

        dot_edge = visitor.graph.get_edge(str(node), str(node.body[0]))[0]
        assert dot_edge.get_label() == 'body[0]'

    def test_multi_parents_node_label(self, visitor):
        node = transformers.ParentChildNodeTransformer().visit(ast.parse('x = 1\nx = 2'))

        visitor.visit(node)

        dot_node = visitor.graph.get_node(str(node.body[0].targets[0]))[0]
        assert dot_node.get_label() == "ast.Name(id='x', ctx=ast.Store())"


class TestSourceGeneratorNodeVisitor(object):
    EOL = '\n'
    SIMPLE_ASSIGN = 'x = 1'
    PASS = 'pass'
    INDENT = ' ' * 4
    CLASS_DEF = 'class Sample:'
    EMPTY_CLASS = CLASS_DEF + EOL + INDENT + PASS
    FUNC_DEF = 'def f():'
    EMPTY_FUNC = FUNC_DEF + EOL + INDENT + PASS
    SINGLE_LINE_DOCSTRING = "''' This is a single line docstring.'''"
    MULTI_LINE_DOCSTRING = "''' This is a multi line docstring." + EOL + EOL + 'Further description...' + EOL + "'''"
    EMBEDDED_QUOTE_DOCSTRING = "'''this is \"double quotes\" inside single quotes'''"
    DOC_FUNC = FUNC_DEF + EOL + INDENT + MULTI_LINE_DOCSTRING
    LINE_CONT = '\\'

    roundtrip_testdata = [
        # assign
        SIMPLE_ASSIGN,
        '(x, y) = z',
        'x += 1',
        'a = b = c',
        '(a, b) = enumerate(c)',
        SIMPLE_ASSIGN + EOL + SIMPLE_ASSIGN,
        SIMPLE_ASSIGN + EOL + EOL + SIMPLE_ASSIGN,
        EMBEDDED_QUOTE_DOCSTRING,
        EOL + SIMPLE_ASSIGN,
        EOL + EOL + SIMPLE_ASSIGN,
        'x = \'string assign\'',

        # class definition
        EMPTY_CLASS,
        EOL + EMPTY_CLASS,
        CLASS_DEF + EOL + INDENT + EOL + INDENT + PASS,
        EMPTY_FUNC,
        EOL + EMPTY_FUNC,
        CLASS_DEF + EOL + INDENT + FUNC_DEF + EOL + INDENT + INDENT + SIMPLE_ASSIGN,
        'class A(B, C):' + EOL + INDENT + PASS,

        # function definition
        FUNC_DEF + EOL + INDENT + PASS,
        'def f(x, y=1, *args, **kwargs):' + EOL + INDENT + PASS,
        'def f(a, b=\'c\', *args, **kwargs):' + EOL + INDENT + PASS,
        FUNC_DEF + EOL + INDENT + 'return',
        FUNC_DEF + EOL + INDENT + 'return 5',
        FUNC_DEF + EOL + INDENT + 'return x == ' + LINE_CONT + EOL + INDENT + INDENT + 'x',

        # yield
        FUNC_DEF + EOL + INDENT + 'yield',
        FUNC_DEF + EOL + INDENT + 'yield 5',

        # importing
        'import x',
        'import x as y',
        'import x.y.z',
        'import x, y, z',
        'from x import y',
        'from x import y, z, q',
        'from x import y as z',
        'from x import y as z, q as p',
        'from . import x',
        'from .. import x',
        'from .y import x',

        # operators
        '(x and y)',
        'x < y',
        'not x',
        'x + y',
        '(x + y) / z',
        '-((-x) // y)',
        '(-1) ** x',
        '-(1 ** x)',
        '0 + 0j',
        '(-1j) ** x',

        # if
        'if x:' + EOL + INDENT + PASS,
        'if x:' + EOL + INDENT + PASS + EOL + 'else:' + EOL + INDENT + PASS,
        'if x:' + EOL + INDENT + PASS + EOL + 'elif y:' + EOL + INDENT + PASS,
        'if x:' + EOL + INDENT + PASS + EOL + 'elif y:' + EOL + INDENT + PASS + EOL + 'else:' + EOL + INDENT + PASS,
        'if x:' + EOL + INDENT + PASS + EOL + 'elif y:' + EOL + INDENT + PASS + EOL + 'elif z:' + EOL + INDENT + PASS,
        'if x:' + EOL + INDENT + PASS + EOL + 'elif y:' + EOL + INDENT + PASS + EOL + 'elif z:' + EOL + INDENT + PASS + EOL + 'else:' + EOL + INDENT + PASS,
        'if x:' + EOL + INDENT + PASS + EOL + 'else:' + EOL + INDENT + 'if y:' + EOL + INDENT + INDENT + PASS + EOL + INDENT + SIMPLE_ASSIGN,
        'x if y else z',
        'y * (z if z > 1 else 1)',
        'if x < y == z < x:' + EOL + INDENT + PASS,
        'if (x < y) == (z < x):' + EOL + INDENT + PASS,
        'if not False:' + EOL + INDENT + PASS,
        'if x:' + EOL + INDENT + PASS + EOL + EOL + 'elif x:' + EOL + INDENT + PASS,  # Double EOL

        # while
        'while not (i != 1):' + EOL + INDENT + SIMPLE_ASSIGN,
        'while True:' + EOL + INDENT + 'if True:' + EOL + INDENT + INDENT + 'continue',
        'while True:' + EOL + INDENT + 'if True:' + EOL + INDENT + INDENT + 'break',
        SIMPLE_ASSIGN + EOL + EOL + 'while False:' + EOL + INDENT + PASS,

        # for
        'for x in y:' + EOL + INDENT + 'break',
        'for x in y:' + EOL + INDENT + PASS + EOL + 'else:' + EOL + INDENT + PASS,

        # try ... except
        'try:' + EOL + INDENT + PASS + EOL + 'except Y:' + EOL + INDENT + PASS,
        'try:' + EOL + INDENT + PASS + EOL + EOL + EOL + 'except Y:' + EOL + INDENT + PASS,
        'try:' + EOL + INDENT + PASS + EOL + 'except Y as y:' + EOL + INDENT + PASS,
        'try:' + EOL + INDENT + PASS + EOL + 'finally:' + EOL + INDENT + PASS,
        'try:' + EOL + INDENT + PASS + EOL + 'except Y:' + EOL + INDENT + PASS + EOL + 'except Z:' + EOL + INDENT + PASS,
        'try:' + EOL + INDENT + PASS + EOL + 'except Y:' + EOL + INDENT + PASS + EOL + 'else:' + EOL + INDENT + PASS,
        'try:' + EOL + INDENT + PASS + EOL + 'except Y:' + EOL + INDENT + PASS + EOL + 'else:' + EOL + INDENT + PASS + EOL + 'finally:' + EOL + INDENT + PASS,

        # del
        'del x',
        'del x, y, z',

        # with
        'with x:' + EOL + INDENT + 'pass',
        'with x as y:' + EOL + INDENT + 'pass',

        # assert
        'assert True, \'message\'',
        'assert True',

        # lambda
        'lambda x: (x)',
        'lambda x: (((x ** 2) + (2 * x)) - 5)',
        'lambda: (1)',
        '(lambda: (yield))()',

        # subscript
        'x[y]',

        # slice
        'x[y:z:q]',
        'x[1:2, 3:4]',
        'x[:2, :2]',
        'x[1:2]',
        'x[::2]',

        # global
        'global x',

        # raise
        'raise Exception()',

        # format
        '\'a %s\' % \'b\'',
        '\'a {}\'.format(\'b\')',
        '(\'%f;%f\' % (point.x, point.y)).encode(\'ascii\')',

        # decorator
        '@x(y)' + EOL + EMPTY_FUNC,
        '@x(y)' + EOL + DOC_FUNC,
        '@x(y)' + EOL + '@x(y)' + EOL + EMPTY_FUNC,
        '@x(y)' + EOL + '@x(y)' + EOL + DOC_FUNC,

        # call
        'f(a)',
        'f(a, b)',
        'f(b=\'c\')',
        'f(*args)',
        'f(**kwargs)',
        'f(a, b=1, *args, **kwargs)',

        # list
        '[]',
        '[1, 2, 3]',

        # dict
        '{}',
        '{a: 3, b: \'c\'}',

        # list comprehension
        'x = [y.value for y in z if y.value >= 3]',

        # generator expression
        '(x for x in y if x)',

        # tuple
        '()',
        '(1,)',
        '(1, 2)',

        # attribute
        'x.y',

        # ellipsis
        'x[...]',

        # str
        "x = 'y'",
        "x = '\"'",
        'x = "\'"',

        # num
        '1',

        # docstring
        SINGLE_LINE_DOCSTRING,
        MULTI_LINE_DOCSTRING,
        CLASS_DEF + EOL + INDENT + MULTI_LINE_DOCSTRING,
        FUNC_DEF + EOL + INDENT + MULTI_LINE_DOCSTRING,
        SIMPLE_ASSIGN + EOL + MULTI_LINE_DOCSTRING,
        MULTI_LINE_DOCSTRING + EOL + MULTI_LINE_DOCSTRING,

        # line continuation
        'x = ' + LINE_CONT + EOL + INDENT + 'y = 5',
        'raise TypeError(' + EOL + INDENT + '\'data argument must be a bytes-like object, not str\')'
    ]

    if utils.check_version(from_inclusive=(2, 7)):
        roundtrip_testdata += [
            # set
            '{1, 2}',

            # set comprehension
            '{x for x in y if x}',

            # dict comprehension
            'x = {y: z for (y, z) in a}',
        ]

    if utils.check_version(to_exclusive=(3, 0)):
        roundtrip_testdata += [
            # print
            'print \'a\'',
            'print \'a\',',
            'print >> sys.stderr, \'a\'',

            # raise with msg and tb
            'raise x, y, z',

            # repr
            '`a`',
        ]

    if utils.check_version(from_inclusive=(3, 0)):
        roundtrip_testdata += [
            # nonlocal
            'nonlocal x',

            # starred
            '*x = y',

            # raise from
            'raise Exception() from exc',

            # byte string
            'b\'byte_string\'',

            # unicode string
            'x = \'äöüß\'',

            # metaclass
            'class X(Y, metaclass=Z):' + EOL + INDENT + 'pass',

            # type hinting
            'def f(a: str) -> str:' + EOL + INDENT + PASS,
            "def f(x: 'x' = 0):" + EOL + INDENT + PASS,
            "def f(x: 'x' = 0, *args: 'args', y: 'y' = 1, **kwargs: 'kwargs') -> 'return':" + EOL + INDENT + PASS,

            # extended iterable unpacking
            '(x, *y) = z',
            '[x, *y, x] = z',

            # kwonly arguments
            'def f(*, x):' + EOL + INDENT + PASS,
            'def f(*, x: int = 5):' + EOL + INDENT + PASS,
            'def f(x, *, y):' + EOL + INDENT + PASS,

            # function definition
            'def f(self, *args, x=None, **kwargs):' + EOL + INDENT + PASS,
        ]

    if utils.check_version(from_inclusive=(3, 3)):
        roundtrip_testdata += [
            # with multiple
            'with x, y:' + EOL + INDENT + 'pass',
            # yield from
            FUNC_DEF + EOL + INDENT + 'yield from x',
        ]

    if utils.check_version(from_inclusive=(3, 5)):
        roundtrip_testdata += [
            # unpack into dict
            '{**kwargs}',

            # async/await
            'async ' + FUNC_DEF + EOL + INDENT + PASS,
            'async ' + FUNC_DEF + EOL + INDENT + 'async for line in reader:' + EOL + INDENT + INDENT + PASS,
            'async ' + FUNC_DEF + EOL + INDENT + 'await asyncio.sleep(1)',
            'async ' + FUNC_DEF + EOL + INDENT + 'async with x:' + EOL + INDENT + INDENT + PASS,

            # matrix multiplication operator
            'x @ y',
        ]

    if utils.check_version(from_inclusive=(3, 6)):
        roundtrip_testdata += [
            # f-strings
            'f\'He said his name is {name}.\'',
            "f'{x!r}'",
            "f'{x!s}'",
            "f'{x!a}'",
            # annotated assignment
            "a: int = 1",
            # dubious annotated assignment of slice
            "x[:]: None = ()",
            # Async list literals & generators
            "[i async for i in some_iterable]",
            "(i async for i in some_iterable)",
        ]

    if utils.check_version(from_inclusive=(3, 8)):
        roundtrip_testdata += [
            # assignment expressions
            'if n := len(a) > 10:' + EOL + INDENT + PASS,
            # positional-only parameters
            'def f(a, /, b, *, c):' + EOL + INDENT + PASS,
            # positional-only parameters with defaults
            'def f(a=1, /, b=2, *, c=3):' + EOL + INDENT + PASS,
        ]

    # add additional tests for semantic testing
    semantic_testdata = list(roundtrip_testdata)

    semantic_testdata += [
        'x = ' + MULTI_LINE_DOCSTRING,
        'b\'\'\'byte string' + EOL + 'next line' + EOL + '\'\'\'',
        r'r"""\a\b\f\n\r\t\v"""',
        'if x:' + EOL + INDENT + PASS + EOL + 'else:' + EOL + INDENT + 'if x:' + EOL + INDENT + INDENT + PASS,
    ]

    if utils.check_version(from_inclusive=(3, 6)):
        semantic_testdata += [
            'raise TypeError(' + EOL + INDENT + 'f"data argument must be a bytes-like object, "' + EOL + INDENT +
            'f"not {type(data).__name__}")',
            'f"a\'b"',
        ]

    @pytest.mark.parametrize("source", roundtrip_testdata)
    def test_codegen_roundtrip(self, source):
        """Check if converting code into AST and converting it back to code yields the same code."""
        node = ast.parse(source)
        generated = visitors.to_source(node)
        print((source, generated))
        assert source == generated

    @pytest.mark.parametrize("source", semantic_testdata)
    def test_codegen_semantic_preservation(self, source):
        """Check if converting code into AST, converting it back to code
        and converting it into an AST again yields the same AST.
        """
        node = ast.parse(source)
        generated = visitors.to_source(node)
        node_from_generated = ast.parse(generated)
        assert ast.dump(node) == ast.dump(node_from_generated)

    def test_fix_linen_umbers(self):
        """Check if an AST with wrong lineno attribute is corrected in the process."""
        node = ast.parse('x = 1' + self.EOL + 'y = 2')
        # set both line numbers to 1
        node.body[1].lineno = 1
        visitors.to_source(node)
        assert node.body[1].lineno == 2
