#!/usr/bin/env python
"""This example was kindly provided by https://github.com/oozie.

This script draws the AST of a Python module as graph with simple points as nodes.
Astmonkey's GraphNodeVisitor is subclassed for custom representation of the AST.

Usage: python3 edge-graph-node-visitor.py some_file.py
"""
import ast
import os
import sys

import pydot

from astmonkey import transformers
from astmonkey.visitors import GraphNodeVisitor


class EdgeGraphNodeVisitor(GraphNodeVisitor):
    """Simple point-edge-point graphviz representation of the AST."""

    def __init__(self):
        super(self.__class__, self).__init__()
        self.graph.set_node_defaults(shape='point')

    def _dot_graph_kwargs(self):
        return {}

    def _dot_node_kwargs(self, node):
        return {}

    def _dot_edge(self, node):
        return pydot.Edge(id(node.parent), id(node))

    def _dot_node(self, node):
        return pydot.Node(id(node), **self._dot_node_kwargs(node))


if __name__ == '__main__':
    filename = sys.argv[1]

    node = ast.parse(open(filename).read())
    node = transformers.ParentChildNodeTransformer().visit(node)
    visitor = EdgeGraphNodeVisitor()
    visitor.visit(node)
    visitor.graph.write(filename + '.dot')
    os.system('sfdp -Tpng -o {} {}'.format(filename + '.png', filename + '.dot'))
