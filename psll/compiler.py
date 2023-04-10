from typing import List, Tuple, Union, Dict, Callable, Optional, cast

from more_itertools import windowed

from functools import partial, reduce
from functools import lru_cache as cached
import operator
from string import ascii_letters

from . import PsllSyntaxError
from .ascii_trees import Pyramid
from . import lexer


def in_pairs(iterable, in_tuple=False):
    """Pair up elements in the array. (s1,s2,s3,s4,s5) -> ((s1,s2),(s3,s4),s5)"""
    for p in windowed(iterable, 2, step=2):
        yield p if p[1] else ((p[0],) if in_tuple else p[0])


# fmt: off
SPACE = " "
PS_KEYWORDS = {"+", "*", "-", "/", "^", "=", "<=>", "out", "chr", "arg", "#",
               '"', "!", "[", "]", "set", "do", "loop", "?"}
# fmt: on


# ==================================================================================================================================================
#
#  ######  #####    #####  #####        ######  #####      ###    ##   ##  #####  #####     ####    ###    ##
#    ##    ##  ##   ##     ##             ##    ##  ##    ## ##   ##   ##  ##     ##  ##   ##      ## ##   ##
#    ##    #####    #####  #####          ##    #####    ##   ##  ##   ##  #####  #####     ###   ##   ##  ##
#    ##    ##  ##   ##     ##             ##    ##  ##   #######   ## ##   ##     ##  ##      ##  #######  ##
#    ##    ##   ##  #####  #####          ##    ##   ##  ##   ##    ###    #####  ##   ##  ####   ##   ##  ######
#
# ==================================================================================================================================================

# _Node = Union[None, str, Tuple]
Node = Union[str, Tuple, None]


def tree_traversal(
    ast: Node,
    *,
    pre_fun: Optional[Callable[[Tuple], Tuple]] = None,
    str_fun: Optional[Callable[[str], Union[Tuple, str]]] = None,
    post_fun: Optional[Callable[[Tuple], Node]] = None,
    final_fun: Optional[Callable[[Tuple], Tuple]] = None,
) -> Node:
    """(Depth-first) walk through the abstract syntax tree and application of appropriate functions"""
    if isinstance(ast, str):
        return str_fun(ast) if str_fun else ast
    elif ast is None:
        return ast
    elif isinstance(ast, tuple):
        ast2: List[Node] = []  # Since, ast is immutable, build a new ast
        for node in ast:
            if node is None:
                ast2.append(node)
            elif isinstance(node, str):
                ast2.append(str_fun(node) if str_fun else node)
            elif isinstance(node, tuple):
                node = pre_fun(node) if pre_fun else node
                node = tree_traversal(
                    node,
                    pre_fun=pre_fun,
                    str_fun=str_fun,
                    post_fun=post_fun,
                    final_fun=final_fun,
                )  # ! Make sure order is correct
                node = cast(Tuple, node)
                node = post_fun(node) if post_fun else node
                ast2.append(node)
            else:
                raise TypeError(
                    "The abstract syntax tree can contain",
                    f"only strings or other, smaller, trees, not {type(node)}",
                )
        return final_fun(tuple(ast2)) if final_fun else tuple(ast2)
    else:
        raise TypeError(
            "The abstract syntax tree can contain",
            f"only strings or other, smaller, trees, not {type(ast)}",
        )


__processing_stack__ = []  # Pre processing functions in order they ought to be applied


def in_processing_stack(fun):
    """Append function to the processing stack"""
    __processing_stack__.append(fun)
    return fun


# ==================================================================================================================================================
#
#   ####  ##   ##   #####   #####    ######  #####  ##     ##        ##     ##    ###    ###    ###  #####   ####
#  ##     ##   ##  ##   ##  ##  ##     ##    ##     ####   ##        ####   ##   ## ##   ## #  # ##  ##     ##
#   ###   #######  ##   ##  #####      ##    #####  ##  ## ##        ##  ## ##  ##   ##  ##  ##  ##  #####   ###
#     ##  ##   ##  ##   ##  ##  ##     ##    ##     ##    ###        ##    ###  #######  ##      ##  ##        ##
#  ####   ##   ##   #####   ##   ##    ##    #####  ##     ##        ##     ##  ##   ##  ##      ##  #####  ####
#
# ==================================================================================================================================================


def find_variable_names(ast):
    """Find all the variable names used in the code"""
    names = set()

    def variable_finder(node: Tuple) -> None:
        if len(node) == 3:
            if node[0] == "set" and isinstance(node[1], str):
                names.add(node[1])

    tree_traversal(ast, post_fun=variable_finder)
    return names


@in_processing_stack
def shorten_variable_names(ast):
    """Shorten variable names to single letter, is possible"""
    names = find_variable_names(ast)
    future_names = set(n for n in names if len(n) == 1)
    rules = {}
    for name in names:
        if len(name) == 1:  # Name is already short
            rules[name] = name
        else:
            all_names = names.union(future_names)
            for letter in name:
                if letter not in all_names:
                    rules[name] = letter
                    future_names.add(letter)
                    break  # Go to the next name
            else:  # No break, aka all single letters in the variable name already used
                for letter in ascii_letters:
                    if letter not in all_names:
                        rules[name] = letter
                        future_names.add(letter)
                        break  # Go to the next name
                else:  # No break, aka all single letter names already taken
                    # Give up and don't shorten the name
                    rules[name] = name
                    future_names.add(name)

    def string_replacer(node):  # Shorten the names
        return rules[node] if node in rules.keys() else node

    return tree_traversal(ast, str_fun=string_replacer)


# =============================================================================================================================
#
#  ####    #####  #####        ##  ##  #####  ##    ##  ##      ##   #####   #####    ####
#  ##  ##  ##     ##           ## ##   ##      ##  ##   ##      ##  ##   ##  ##  ##   ##  ##
#  ##  ##  #####  #####        ####    #####    ####    ##  ##  ##  ##   ##  #####    ##  ##
#  ##  ##  ##     ##           ## ##   ##        ##     ##  ##  ##  ##   ##  ##  ##   ##  ##
#  ####    #####  ##           ##  ##  #####     ##      ###  ###    #####   ##   ##  ####
#
# =============================================================================================================================


def apply_replacement_rules(ast: Tuple, rules: Dict[str, Tuple]) -> Tuple:
    """Apply replacement rules to the abstract syntax tree"""

    def singleton_tuple_replacer(node: Tuple) -> Tuple:  # Replace (f) by def of f
        return rules[node[0]] if len(node) == 1 and node[0] in rules.keys() else node

    def string_replacer(node: str) -> Union[Tuple, str]:  # Replace f by def of f
        return rules[node] if node in rules.keys() else node

    ast2 = tree_traversal(
        ast, pre_fun=singleton_tuple_replacer, str_fun=string_replacer
    )

    return cast(Tuple, ast2)


@in_processing_stack
def def_keyword(ast):
    """Search for ('def','something',(...)) keywords"""

    defs: List[Tuple[str, Tuple]] = []

    def replacer(node: str) -> Node:
        if len(defs) > 0:
            for value, definition in reversed(defs):
                if node == value:
                    return definition
        return node

    def find_defs(node: Tuple) -> Tuple:
        if len(node) > 0 and node[0] == "def":
            if not len(node) == 3:
                raise PsllSyntaxError(
                    f"'def' statement must have 3 members, not {len(node)} (node = {node})"
                )
            key, value = node[1], node[2]
            if not isinstance(key, str):
                raise PsllSyntaxError(
                    f"'def' statement can only assign keys to brackets. Got type {type(key)} for key"
                )
            if key == "def":
                raise PsllSyntaxError("('def' 'def' (...)) structure is not allowed")
            if not isinstance(value, tuple):
                raise PsllSyntaxError(
                    f"'def' statement can only assign keys to brackets. Got type {type(value)} for bracket"
                )
            defs.append((key, apply_replacement_rules(value, dict(defs))))
            return ()  # Return empty tuple
        return node

    def pop_def_stack(ast: Tuple) -> Tuple:
        for node in ast:
            if node == ():
                defs.pop()
        return ast

    return tree_traversal(
        ast, str_fun=replacer, pre_fun=find_defs, final_fun=pop_def_stack
    )


# =======================================================================================
#
#    ###    #####    #####      ###    ##    ##   ####
#   ## ##   ##  ##   ##  ##    ## ##    ##  ##   ##
#  ##   ##  #####    #####    ##   ##    ####     ###
#  #######  ##  ##   ##  ##   #######     ##        ##
#  ##   ##  ##   ##  ##   ##  ##   ##     ##     ####
#
# =======================================================================================


@in_processing_stack
def range_keyword(ast):
    def ranger(node: Tuple) -> Tuple:
        if len(node) > 0 and node[0] == "range":
            if not all(map(lambda x: isinstance(x, str), node[1:])):
                raise PsllSyntaxError("'range' arguments must be integer literals")
            if len(node) > 4:
                raise PsllSyntaxError(
                    "'range' must be of the form (range begin end) or (range begin end"
                    " step)"
                )
            start, stop = int(node[1]), int(node[2]) + 1
            step = int(node[3]) if len(node) == 4 else 1
            return ("[" + ", ".join(map(str, range(start, stop, step))) + "]",)
        return node

    return tree_traversal(ast, pre_fun=ranger)


# @in_processing_stack
# def len_keyword(ast):

#     def lengther(node):
#         if len(node)==3 and node[0]=='len':
#             if not all(map(is_string,node[1:])):
#                 raise PsllSyntaxError(f"'range' arguments must be variable names")
#             # return
#             a, N = node[1], node[2]
#             ('set',N,0) ('loop', (), ())
#             # ( (set N 0) (loop (! (= (arg a N) nil)) (set N (+ N 1))) )

#     return tree_traversal(ast,pre_fun=lengther)


# TESTED
@in_processing_stack
def expand_array_literals(ast):
    def one_element_array(element):
        """Put `element` into a one-element array with the subtraction trick"""
        return (
            ("-", (element, "0"), ("0", "0"))
            if element != "0"
            else ("-", (element, "1"), ("1", "1"))
        )

    def array_to_tree(string):
        """Parse (inner) array string to its ast tree representation"""
        elements = lexer.split(string)  # Reuse lexer split
        if not elements:
            return ("-", ("0", "0"), ("0", "0"))  # Return empty array

        # Build the tree
        if len(elements) % 2:
            tree = one_element_array(elements[-1])
            elements = elements[:-1]
        else:
            tree = ()
        if elements:
            for e2, e1 in windowed(reversed(elements), 2, step=2):
                tree = ("+", (e1, e2), tree) if tree else (e1, e2)

        return tree

    def array_expander(string):
        if lexer.in_context(string, "[]"):
            return array_to_tree(string[1:-1])
        return string

    return tree_traversal(ast, str_fun=array_expander)


# =========================================================================================
#
#   ####  ######  #####    ##  ##     ##   ####     ####
#  ##       ##    ##  ##   ##  ####   ##  ##       ##
#   ###     ##    #####    ##  ##  ## ##  ##  ###   ###
#     ##    ##    ##  ##   ##  ##    ###  ##   ##     ##
#  ####     ##    ##   ##  ##  ##     ##   ####    ####
#
# =========================================================================================

# TESTED
@in_processing_stack
def expand_string_literals(ast):

    string_split = partial(
        lexer.context_split, delimiter="", contexts=('""',), remove_empty=True
    )

    def special(char):
        """Convert char to its special character representation"""
        cases = {"n": "\n", "t": "\t", "r": "\r"}
        return cases[char] if char in cases else char

    def expand(string):
        if lexer.in_context(string, '""'):
            tree = ()
            for char in string_split(string[1:-1]):
                if len(char) > 1 and char[0] == "\\":
                    char = special(char[1])
                subtree = ("chr", "_", str(ord(char)))
                tree = subtree if not tree else ("+", tree, subtree)
            # TODO Is there a more robust way of making an empty string in pyramid scheme??
            if not tree:
                tree = ("eps",)
            return tree
        return string

    return tree_traversal(ast, str_fun=expand)


# =============================================================================================================================================
#
#   #####   ##   ##  #####  #####  ##   ##  ##      ##             ####   #####   ###    ###  ###    ###
#  ##   ##  ##   ##  ##     ##     ##   ##  ##      ##            ##     ##   ##  ## #  # ##  ## #  # ##
#  ##   ##  ##   ##  #####  #####  ##   ##  ##      ##            ##     ##   ##  ##  ##  ##  ##  ##  ##
#  ##   ##   ## ##   ##     ##     ##   ##  ##      ##            ##     ##   ##  ##      ##  ##      ##
#   #####     ###    #####  ##      #####   ######  ######         ####   #####   ##      ##  ##      ##  ##
#
# =============================================================================================================================================


@in_processing_stack
def expand_overfull_outs(ast):
    def expander(node: Tuple) -> Tuple:
        if len(node) > 3 and node[0] == "out":
            return tuple(("out", *p) for p in in_pairs(node[1:], in_tuple=True))
        return node

    return tree_traversal(ast, pre_fun=expander)


binary_operators = set(("+", "-", "*", "/", "^", "=", "<=>"))


@in_processing_stack
def expand_left_associative(ast):
    def expander(node: Tuple) -> Tuple:
        if len(node) > 3 and node[0] in binary_operators:
            tree = node[:3]
            for element in node[3:]:
                tree = (node[0], tree, element)
            return cast(Tuple, tree)
        return node

    return tree_traversal(ast, pre_fun=expander)


@in_processing_stack
def expand_right_associative(ast):
    def expander(node: Tuple) -> Tuple:
        if len(node) > 2 and node[-1] in binary_operators:
            tree = node[-1:-4:-1]
            # (node[-1], node[-2], node[-3])
            for element in reversed(node[:-3]):
                tree = (node[-1], element, tree)
            return cast(Tuple, tree)
        return node

    return tree_traversal(ast, pre_fun=expander)


# =============================================================================================================
#
#  #####    #####    ####  ######            #####   #####     #####    ####
#  ##  ##  ##   ##  ##       ##              ##  ##  ##  ##   ##   ##  ##
#  #####   ##   ##   ###     ##    ########  #####   #####    ##   ##  ##
#  ##      ##   ##     ##    ##              ##      ##  ##   ##   ##  ##
#  ##       #####   ####     ##              ##      ##   ##   #####    ####
#
# =============================================================================================================

# TESTED
@in_processing_stack
def expand_overfull_brackets(ast):
    """Expand lists of many lists into lists of length 2"""

    def expander(node: Tuple) -> Tuple:
        if all(map(lambda x: isinstance(x, tuple), node)):
            while len(node) > 2:
                node = tuple(p for p in in_pairs(node))
        elif len(node) > 3:
            raise PsllSyntaxError(
                "Invalid bracket structure. Can only expand lists of lists."
            )
        return node

    return tree_traversal(ast, post_fun=expander)


@in_processing_stack
def fill_in_empty_trees(ast):
    """Fill in the implicit empty strings in brackets with only lists"""

    def filler(node: Tuple) -> Node:
        if node == ():  # Empty node
            return ""
        elif all(map(lambda x: isinstance(x, tuple), node)):  # All tuples
            return ("", *node)
        elif node[0] == "_":
            return ("", *node)
        elif node[0] in PS_KEYWORDS:
            return node  # Don't add a pad before psll keywords
        else:
            return (
                "",
                *node,
            )  # Add pad before non-keywords (this allows one to make arrays)

    return tree_traversal(ast, post_fun=filler)


@in_processing_stack
def fill_in_underscores(ast):
    def filler(node: Tuple) -> Tuple:
        if len(node) == 3:
            if isinstance(node[1], str) and node[1] != "_":
                node = (node[0], (node[1], "_", "_"), node[2])
            if isinstance(node[2], str) and node[2] != "_":
                node = (node[0], node[1], (node[2], "_", "_"))
        elif len(node) == 2:
            if isinstance(node[1], str) and node[1] != "_":
                node = (node[0], (node[1], "_", "_"), "_")
            else:
                node = (*node, "_")
        elif len(node) == 1 and node[0] != "_":
            node = (*node, "_", "_")
        return node

    return tree_traversal(ast, post_fun=filler)


@in_processing_stack
def underscore_keyword(ast):
    def replacer(node: str) -> Union[str, None]:
        return None if node == "_" else node

    return tree_traversal(ast, str_fun=replacer)


def apply_processing_stack(ast: Node, full_names: bool = False) -> Node:
    """Apply the processing stack to the ast"""
    stack = __processing_stack__[1:] if full_names else __processing_stack__
    return reduce(lambda x, y: y(x), [ast] + list(stack))  # type: ignore


# =========================================================================================
#
#   ####   #####   ###    ###  #####   ##  ##      #####
#  ##     ##   ##  ## #  # ##  ##  ##  ##  ##      ##
#  ##     ##   ##  ##  ##  ##  #####   ##  ##      #####
#  ##     ##   ##  ##      ##  ##      ##  ##      ##
#   ####   #####   ##      ##  ##      ##  ######  #####
#
# =========================================================================================


@cached(maxsize=10000)
def build_tree(ast):
    """Build the call tree from the leaves to the root"""

    if isinstance(ast, str):
        return Pyramid.from_text(ast)
    elif ast is None:
        return None
    elif isinstance(ast, tuple):
        if len(ast) != 3:
            raise RuntimeError(
                f"Invalid structure of the abstract syntax tree. ({ast})"
            )
        if not isinstance(ast[0], str):
            raise RuntimeError(
                "Invalid abstract syntax tree. The first element of each node must be"
                f" a string, not a {type(ast[0])}"
            )
        return build_tree(ast[0]) + (build_tree(ast[1]), build_tree(ast[2]))
    else:
        raise TypeError(
            "Abstract syntax tree must be represented by a list (or just a string) not"
            f" a {type(ast)}"
        )


# TODO Refactor
def compile(ast) -> str:
    """Compile text into trees"""
    program = str(reduce(operator.add, (build_tree(a) for a in ast)))
    # Remove excessive whitespace
    return "\n".join(line[1:].rstrip() for line in program.split("\n"))
