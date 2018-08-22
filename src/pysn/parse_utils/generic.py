#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Generic parser using lark-parser.

Subclass :class:`GenericParser` (remember to set :attr:`GenericParser.grammar`
to point to your grammar file) to define a powerful parser.

(Optional) Subclass :class:`AttrTree` and :class:`AttrToken` (and set
:attr:`GenericParser.AttrTree` and :attr:`GenericParser.AttrTree.AttrToken`).

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
"""

import logging
from inspect import signature
from pathlib import Path

from lark import Lark
from lark import Transformer
from lark import Tree
from lark.lexer import Token

from . import prettyprint


def item_rule(item):
    """Rule of a tree or token"""
    try:
        return item.data
    except AttributeError:
        try:
            return item.type
        except AttributeError:
            return ''


def new_item(rule):
    """Create empty Tree or Token (if rule is upper case only)"""
    if rule == rule.upper():
        return Token(rule, '')
    return Tree(rule, [])


class AttrToken(Token):
    """
    Token with attribute access.

    Created by :method:`AttrTree.transform`, from :class:`lark.lexer.Token`
    (see 'token' argument of :method:`__new__`).

    Override this and :class:`AttrTree` if you need special behaviour for your
    implementation (subclass) of :class:`GenericParser`.

    Attributes:
        rule (str): Rule name (in common with :class:`AttrTree`).
        eval: Transformed data type (in common with :class:`AttrTree`).
    """

    __slots__ = ('rule', 'eval')

    @classmethod
    def transform(cls, token, *args, **kwargs):

        sig = signature(super().__init__)
        opt = dict(type_=token.type, value=token.value, pos_in_stream=token.pos_in_stream,
                   line=token.line, column=token.column)
        opt.update(sig.bind_partial(*args, **kwargs).arguments)

        self = super(AttrToken, cls).__new__(cls, **opt)
        self.rule = self.type
        if token.type == 'INT':
            self.eval = int(self.value)
        elif token.type == 'NUMERIC':
            self.eval = float(self.value)
        else:
            self.eval = str(self.value)
        return self

    def replace(self, value):
        """Returns new Token (of same rule) with value replaced."""
        return type(self)(self, value=value)

    def str_repr(self):
        return repr(str(self))[1:-1]

    def __repr__(self):
        return '%s(%s) %s' % (self.__class__.__name__, self.rule, repr(str(self)))


class NoSuchRuleException(AttributeError):
    """Rule not found exceptions"""
    def __init__(self, rule, tree=None):
        try:
            post = ' (%s)' % (repr(tree.rule),)
        except AttributeError:
            post = ''
        super().__init__('no %s child in tree%s' % (repr(rule), post))


class AttrTree(Tree):
    """
    Tree with attribute access.

    Created in :method:`GenericParser.parse` by :method:`transform`, from
    :class:`lark.Tree`.

    Override this and :class:`.AttrToken` if you need special behaviour for
    your implementation (subclass) of :class:`GenericParser`.

    Attributes:
        rule: Rule name (in common with :class:`.AttrToken`).
        rules: All rule names (for :attr:`.children`).
        eval: Transformed data type (in common with :class:`.AttrToken`).
        _attrtoken: :class:`AttrToken` implementation.
    """

    @classmethod
    def transform(cls, tree, *args, **kwargs):
        self = cls.__new__(cls)

        sig = signature(super().__init__)
        opt = dict(data=tree.data, children=tree.children, meta=tree._meta)
        opt.update(sig.bind_partial(*args, **kwargs).arguments)

        type(self)._attrset(self, 'data', opt['data'])
        children = []
        for i, child in enumerate(opt['children'].copy()):
            if isinstance(child, Tree):
                node = cls.transform(tree=child)
            elif isinstance(child, Token):
                node = cls._attrtoken.transform(token=child)
            else:
                node = cls._attrtoken('STR', str(child))
            children += [node]
        type(self)._attrset(self, 'children', children)
        type(self)._attrset(self, '_meta', opt['meta'])

        return self

    @classmethod
    def from_dict(cls, key_val):
        try:
            keys, values = zip(*key_val.items())
        except AttributeError:
            try:
                keys, values = zip(*key_val)
            except TypeError:
                raise TypeError("arg 'key_val' (%s) not dict (or iterable of key-value pairs)" %
                                (key_val.__class__.__name__,)) from None
        items = []
        for key, val in zip(keys, values):
            if key == key.upper():
                item = [cls._attrtoken(key, val)]
            else:
                item = [cls(key, cls.from_dict(val))]
            items += item
        if len(items) == 1:
            return items[0]
        else:
            return items

    """AttrToken implementation."""
    _attrtoken = AttrToken

    # -- public interface ----------------------------------------------
    @property
    def rule(self):
        """Returns this rule (tree)"""
        return self.data

    @property
    def rules(self):
        """Returns all rules (children)"""
        return [node.rule for node in self.children]

    @property
    def eval(self):
        """Returns self (the tree)"""
        return self

    def find(self, rule):
        """Gets first child matching rule, or None if none"""
        return self._getchild_(rule, multi=False)

    def all(self, rule):
        """Gets all children matching rule, or [] if none"""
        return self._getchild_(rule, multi=True)

    def set_child(self, rule, value):
        """Sets first child matching rule (raises if none)"""
        self._setchild_(rule, value)

    def tree_walk(self):
        """Generator for (depth-first, i.e. parse order) iter over children"""
        for child in self.children:
            yield child
            try:
                yield from child.tree_walk()
            except AttributeError:
                continue

    def set(self, value, rule=None):
        """Sets value for first token matching rule (or leaf if None)"""
        if rule:
            token = self.find(rule)
        else:
            if not len(self.children) == 1:
                raise AssertionError('no rule but node not leaf (ambigiuous)')
            token = self.children[0]
            rule = token.rule
        try:
            new = token.replace(value)
        except AttributeError as e:
            raise TypeError('child not a token: %s' % (repr(token),)) from e
        self.set_child(rule, new)

    def str_repr(self):
        return repr(str(self))[1:-1]

    def treeprint(self, content=True, indent=''):
        """Formats tree structure (for grammar debugging purposes)"""
        lines = str(prettyprint.transform(self, content)).splitlines()
        print('\n'.join(indent + line for line in lines))

    # -- private methods -----------------------------------------------
    def __len__(self):
        return len(self.children)

    def _getchild_(self, rule, multi=False):
        found = []
        for child in type(self)._attrget(self, 'children'):
            if type(self)._attrget(child, 'rule') == rule:
                if not multi:
                    return child
                found += [child]
        if not multi:
            return None
        return found

    def _setchild_(self, rule, value):
        for i, child in enumerate(self.children):
            if type(self)._attrget(child, 'rule') == rule:
                return self._safeset_child_item(i, value)
        raise NoSuchRuleException(rule, self)

    def __getitem__(self, item):
        return self.children[item].eval

    def __setattr__(self, attr, value):
        if attr in dir(self):
            return type(self)._attrset(self, attr, value)
        self._setchild_(attr, value)

    def __getattr__(self, attr):
        if attr in dir(self):
            return type(self)._attrget(self, attr)
        child = self._getchild_(attr)
        if child is None:
            raise NoSuchRuleException(attr, self)
        return child.eval

    def _safeset_child_item(self, item, value):
        children = type(self)._attrget(self, 'children')
        children[item] = value
        type(self)._attrset(self, 'children', children)

    @classmethod
    def _attrget(cls, obj, attr):
        return object.__getattribute__(obj, attr)

    @classmethod
    def _attrset(cls, obj, attr, value):
        return object.__setattr__(obj, attr, value)

    def __str__(self):
        children = type(self)._attrget(self, 'children')
        return ''.join(str(x) for x in children)

    def __repr__(self):
        return '%s(%s) %s' % (self.__class__.__name__, self.rule, repr(str(self)))


class PreParser(Transformer):
    """
    Pre-parsing transformer to shape tree (after initial AST).

    Methods after rule's (Tree's or Token's) will be visited by the Lark parser visitor, with
    children as argument, and the return value replaces).
    """

    # -- public interface ----------------------------------------------
    @classmethod
    def first(cls, rule, tree_or_items):
        """Returns first item in tree or list, matching rule"""
        return cls._find(rule, tree_or_items, 'single')

    @classmethod
    def split(cls, rule, tree_or_items):
        """Splits tree or list on rule, into tuple (pre, match, post)"""
        return cls._find(rule, tree_or_items, 'split')

    @classmethod
    def all(cls, rule, tree_or_items):
        """Returns all items in tree or list, matching rule"""
        return cls._find(rule, tree_or_items, 'all')

    @classmethod
    def flatten(cls, tree_or_items):
        """Flattens tree or list into list"""
        items = []
        for item in cls._as_items(tree_or_items):
            try:
                items += item
            except TypeError:
                items += [item]
        return items

    # -- private methods -----------------------------------------------
    @classmethod
    def _as_items(cls, tree_or_items):
        try:
            return list(tree_or_items)
        except TypeError:
            try:
                return tree_or_items.children
            except AttributeError:
                return [tree_or_items]

    @classmethod
    def _find(cls, rule, tree_or_items, mode):
        split = (mode == 'split')
        first, found = None, []
        if split:
            pre, post = [], []
        elif mode != 'all':
            first = True
        for item in cls._as_items(tree_or_items):
            m = (item_rule(item) == rule)
            if m and first:
                return item
            elif split:
                if not first and m:
                    first = item
                elif not first:
                    pre.append(item)
                else:
                    post.append(item)
            else:
                found.append(item)
        if split:
            return (pre, first, post)
        elif not first:
            return found


class GenericParser:
    """
    Generic parser using lark-parser.

    Meant to be inherited for defining specific parsers (say, ThetaRecordParser for NONMEM API).
    Will do the following:

    1. Lex and parse a 'buffer' (str, not bytes!) using Lark (see Lark_) and (from file in
        ``grammar`` attribute), to build AST.
    2. Transform tree with transformer (see :class:`PreParser`).
    3. Convert to :class:`AttrTree` for tree traversal (attribute access magic)

    Attributes:
        non_empty (list): Insert empty placeholders if missing. Dict map of rule -> (pos, name),
            where a Tree or Token (if uppercase) will be inserted at 'pos' of the children of
            'rule', if none exists.
        buffer (str): Buffer parsed (see :method:`parse`).
        grammar (str): Path to grammar file. Set in subclass.
        root (str): Root of final tree (instance of :class:`AttrTree`)
        _attrtree: AttrTree implementation used in :method:`parse` (step 3)

    .. _Lark:
        https://github.com/lark-parser/lark
    """

    """Children (of rules) to create placeholder for if missing"""
    non_empty = []

    """Pre-parsing transformer"""
    _transformer = None

    """:class:`AttrTree` implementation."""
    _attrtree = AttrTree

    lark_options = dict(
        keep_all_tokens=True,
        parser='earley',
        start='root',
    )

    def __init__(self, buf=None, **lark_options):
        """
        Args:
            buf (str): Buffer (to parse immediately; see :method:`parse`)
            **lark_options: Options to `:class:Lark`. These defaults can be overriden:

                * ``keep_all_tokens=True``
                * ``parser='earley'``
                * ``propagate_positions=True``
        """
        self.lark_options.update(lark_options)
        if self._transformer:
            self.lark_options['transformer'] = self._transformer
        self.root = self.parse(buf)

    def parse(self, buf):
        """
        Parses a buffer, transforms and constructs :class:`AttrTree` object.

        Args:
            buf (str): Buffer to parse.
        """
        self.buffer = buf
        if self.buffer is None:
            return None

        grammar = Path(self.grammar).resolve()
        with open(str(grammar), 'r') as fh:
            self.lark = Lark(fh, **self.lark_options)
            root = self.lark.parse(self.buffer)

        if self.non_empty:
            root = self.insert(root, self.non_empty)
        return self._attrtree.transform(tree=root)

    def __str__(self, content=True):
        if not self.root:
            return repr(self)
        lines = str(prettyprint.transform(self.root, content)).splitlines()
        return '\n'.join(lines)

    @classmethod
    def insert(cls, item, non_empty):
        """
        Inserts missing Tree/Token amongst children (see :attr:`non_empty`).

        Args:
            item: Tree to recurse.
            non_empty: Dict of rule -> (pos, name) tuple.
        """
        if not non_empty or isinstance(item, Token):
            return item
        try:
            pos, name = non_empty[item_rule(item)]
        except KeyError:
            pass
        else:
            if not any(item_rule(child) == name for child in item.children):
                item.children.insert(pos, new_item(name))
        for i, child in enumerate(item.children):
            item.children[i] = cls.insert(child, non_empty)
        return item
