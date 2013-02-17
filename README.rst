astmonkey
---------

``astmonkey`` is a set of tools to work with Python AST.

Installation
------------

The easiest way to install ``astmonkey`` is clone this repository and use ``setup.py``:

::

    $ hg clone https://khalas@bitbucket.org/khalas/astmonkey
    $ cd astmonkey
    $ python setup.py install

``astmonkey.transformers.ParentNodeTransformer``
------------------------------------------------

This transformer adds few fields to every node in AST:
 * ``parent`` - link to parent node,
 * ``parents`` - list of all parents (only ``ast.expr_context`` nodes have more than one parent node, in other causes this is one-element list),
 * ``parent_field`` - name of field in parent node including child node,
 * ``parent_field_index`` - parent node field index, if it is a list.

Example usage:

.. include:: examples/parent_node_transformer.py 
   :literal:

``astmonkey.visitors.GraphNodeVisitor``
---------------------------------------

This visitor creates Graphviz graph from Python AST (via ``pydot``). Before you use 
``astmonkey.visitors.GraphNodeVisitor`` you need to add parents links to tree nodes 
(with ``astmonkey.transformers.ParentNodeTransformer``).

Example usage:

.. include:: examples/graph_node_visitor.py 
   :literal:

Produced ``graph.png``:

.. image:: examples/graph.png

``astmonkey.utils.is_docstring``
--------------------------------

This routine checks if target node is a docstring. Before you use 
``astmonkey.utils.is_docstring`` you need to call ``astmonkey.transformers.ParentNodeTransformer.visit``.

Example usage:

.. include:: examples/is_docstring.py 
   :literal:

