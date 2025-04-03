import os
import random
import sys
from collections.abc import Iterator

# from itertools import product, permutations
from contextlib import contextmanager
from functools import partial
from string import ascii_letters
from typing import Any, Callable, Optional, TypeVar

import pytest

# Add '.' to path so running this file by itself also works
sys.path.append(os.path.realpath("."))

from conftest import Subtests

import psll
import psll.macros

Leaf = psll.macros.Leaf
Node = psll.macros.Node


def depth(tree: Node) -> int:
    """Calculate the depth of a tree"""
    if isinstance(tree, str):
        return 0
    elif isinstance(tree, tuple):
        if len(tree) == 0:
            return 0
        else:
            return max(depth(node) for node in tree) + 1
    else:
        raise TypeError(
            f"The abstract syntax tree can contain only strings or other, smaller, trees, not {type(tree).__name__}"
        )


random_string = lambda N: "".join(random.choice(ascii_letters) for _ in range(N))


# spell-checker: words prob
def random_tree(max_depth: int = 10, str_prob: float = 0.6) -> Node:
    """Make up a random tree"""
    ast: list[Node]
    ast = [random_string(random.randrange(4))]
    for _ in range(2):
        node: Node
        if random.random() < str_prob or max_depth == 1:
            node = random_string(random.randrange(4))
        else:
            node = random_tree(max_depth=max_depth - 1)
        ast.append(node)
    return tuple(ast)


@contextmanager
def psll_file(content: str, filename: Optional[str] = None) -> Iterator[str]:
    """Mock a .psll file with certain content"""
    if not filename:  # Make temp filename
        filename = f"temp_{random_string(10)}.psll"
    try:
        with open(filename, "w") as f:
            f.write(content)
        yield filename
    finally:
        os.remove(filename)


_T = TypeVar("_T")
_V = TypeVar("_V")


# class MetaTests:
def paired_test(subtests: Subtests, inputs: list[_T], targets: list[_V], fun: Callable[[_T], _V]) -> None:
    """Test input/target pairs with fun(input)==target"""
    # self.assertEqual(len(inputs), len(targets))
    assert len(inputs) == len(targets)
    for i, t in zip(inputs, targets):
        with subtests.test(input=i):
            assert fun(i) == t


def single_test(subtests: Subtests, inputs: list[_T], fun: Callable[[_T], Any]) -> None:
    """Test input with fun(input)"""
    for i in inputs:
        with subtests.test(input=i):
            fun(i)


def error_test(
    subtests: Subtests,
    inputs: list[_T],
    fun: Callable[[_T], Any],
    error: type[Exception],
) -> None:
    """Test that text throws an error"""
    for i in inputs:
        with subtests.test(input=i), pytest.raises(error):
            fun(i)


# ==========================================================================================================
#
#  #####  ##  ##      #####        ##  ##     ##  #####   ##   ##  ######
#  ##     ##  ##      ##           ##  ####   ##  ##  ##  ##   ##    ##
#  #####  ##  ##      #####        ##  ##  ## ##  #####   ##   ##    ##
#  ##     ##  ##      ##           ##  ##    ###  ##      ##   ##    ##
#  ##     ##  ######  #####        ##  ##     ##  ##       #####     ##
#
# ==========================================================================================================


def read_file(content: str) -> str:
    """read_file + preprocess"""
    with psll_file(content) as f:
        text = psll.preprocessor.read_file(f)
        return psll.preprocessor.preprocess(text)


def test_read_file_empty(subtests: Subtests) -> None:
    """> Read and parse files with empty brackets"""
    contents = ["", "()", "( )", "()()", "()()()", "(())", "() (())"]
    targets = ["", "()", "()", "() ()", "() () ()", "(())", "() (())"]
    paired_test(subtests, contents, targets, read_file)


def test_read_file_simple(subtests: Subtests) -> None:
    """> Read and parse files with simple contents"""
    contents = [
        "(set)",
        "(hi)",
        "(set 1)",
        "(set hi 1)",
        "(1 2 3 4)",
        "(hi) (salut)",  # spell-checker: disable-line
    ]
    paired_test(subtests, contents, contents, read_file)


def test_read_file_comments(subtests: Subtests) -> None:
    """> Removing comments"""
    contents = [
        "// hi",
        "() // hi",
        "(\n// hi\n)",
        "//(\n()",
        "()\n//)",
        "// hi\n()\n// hi",
        "//()",
    ]
    targets = ["", "()", "()", "()", "()", "()", ""]
    paired_test(subtests, contents, targets, read_file)


@pytest.mark.skip(reason="Needs work")
def test_read_file_single_spaces(subtests: Subtests) -> None:
    """> Only single spaces"""
    contents = ["( )", "(  )", "(   )", "(     )"]
    targets = ["()", "()", "()", "()"]
    paired_test(subtests, contents, targets, read_file)


@pytest.mark.skip("Needs work")
def test_read_file_leading_and_trailing_spaces(subtests: Subtests) -> None:
    """> No leading or trailing whitespace"""
    contents = ["(   hi)", "(hi   )", "(hi   1)", "(   hi 1)", "(hi 1   )"]
    targets = ["(hi)", "(hi)", "(hi 1)", "(hi 1)", "(hi 1)"]
    paired_test(subtests, contents, targets, read_file)


def test_read_file_multiline(subtests: Subtests) -> None:
    """> Input over multiple lines"""
    contents = ["()\n()", "\n(hi)", "(\nhi)", "(hi\n)", "(hi)\n"]
    targets = ["() ()", "(hi)", "(hi)", "(hi)", "(hi)"]
    paired_test(subtests, contents, targets, read_file)


# =============================================================
#
#  ##      #####  ##    ##
#  ##      ##      ##  ##
#  ##      #####    ####
#  ##      ##      ##  ##
#  ######  #####  ##    ##
#
# =============================================================


# @pytest.skip("Needs rewriting into tests of `lex`")
# class Split(unittest.TestCase, MetaTests):
#     def test_simple(self):
#         """> Simple inputs"""
#         texts = ["", "()", "() ()", "(hi)", "(out 1)", "(set a 1)"]
#         targets = [(), ("()",), ("()", "()"), ("(hi)",), ("(out 1)",), ("(set a 1)",)]
#         self.paired_test(texts, targets, psll.macros.split_into_lines)

#     def test_nested(self):
#         """> Nested inputs"""
#         texts = ["(())", "(()) ()", "(((hi)))", "(() () hi)", "(() ()) (()) ()"]
#         targets = [
#             ("(())",),
#             ("(())", "()"),
#             ("(((hi)))",),
#             ("(() () hi)",),
#             ("(() ())", "(())", "()"),
#         ]
#         self.paired_test(texts, targets, psll.macros.split_into_lines)

#     def test_error(self):
#         """> Bracket parity and ketbra errors"""
#         texts = ["(", ")", ")(", "(hi))", "((hi)", "((", "))", "((()())", "(()()))"]
#         self.error_test(texts, psll.macros.split_into_lines, psll.macros.PsllSyntaxError)

#     def test_simple_subtrees(self):
#         """> Simple subtrees"""
#         texts = ["(hi)", "(set a 1)", "(one two three four)"]
#         targets = [("hi",), ("set", "a", "1"), ("one", "two", "three", "four")]
#         self.paired_test(texts, targets, psll.split_into_subtrees)

#     def test_nested_subtrees(self):
#         """> Nested subtrees"""
#         texts = ["(set a (= b 1))", "(a (b (() c)))"]
#         targets = [("set", "a", ("=", "b", "1")), ("a", ("b", (("",), "c")))]
#         self.paired_test(texts, targets, psll.split_into_subtrees)

#     def test_blank(self):
#         """> Trees with blank elements"""
#         texts = ["()", "(())", "(() hi)", "(1 2)", "((hi 1) (hi 2))"]
#         targets = [
#             ("",),
#             (("",),),
#             (("",), "hi"),
#             ("1", "2"),
#             (("hi", "1"), ("hi", "2")),
#         ]
#         self.paired_test(texts, targets, psll.split_into_subtrees)

#     def test_quotes(self):
#         """> Don't split quotes"""
#         texts = ['("hi")', '(set a "one")', '("string with spaces")']
#         targets = [('"hi"',), ("set", "a", '"one"'), ('"string with spaces"',)]
#         self.paired_test(texts, targets, psll.split_into_subtrees)

#     @pytest.skip("Currently broken")
#     def test_double_quote_command(self):
#         """> Make sure " command is not broken (aka it does not start an unnecessary string)"""
#         pass


# ======================================================================================================================
#
#  ######  #####    #####  #####        ######  #####      ###    ##   ##  #####  #####     ####    ###    ##
#    ##    ##  ##   ##     ##             ##    ##  ##    ## ##   ##   ##  ##     ##  ##   ##      ## ##   ##
#    ##    #####    #####  #####          ##    #####    ##   ##  ##   ##  #####  #####     ###   ##   ##  ##
#    ##    ##  ##   ##     ##             ##    ##  ##   #######   ## ##   ##     ##  ##      ##  #######  ##
#    ##    ##   ##  #####  #####          ##    ##   ##  ##   ##    ###    #####  ##   ##  ####   ##   ##  ######
#
# ======================================================================================================================

count = 0


def counter(node: _T) -> _T:
    global count
    count += 1
    return node


def test_tree_traveral_string_fun(subtests: Subtests) -> None:
    """> Test that the string function is applied a correct number of times"""
    trees = [
        ("a",),
        ("a", "b"),
        ("a", "b", "c"),
        ("a", ("b", "c"), "d"),
        (
            "Quick",
            (("brown", "fox"), ("jumped", (("over",),)), "a"),
            ("lazy",),
            "dog",
        ),
    ]
    counts = [1, 2, 3, 4, 8]

    def count_strings(tree: Node) -> int:
        global count
        count = 0
        psll.macros.tree_traversal(tree, str_fun=counter)
        return count

    paired_test(subtests, trees, counts, count_strings)


def test_tree_traveral_pre_fun(subtests: Subtests) -> None:
    trees = [
        ("a",),
        ("a", "b"),
        ("a", "b", "c"),
        ("a", ("b", "c"), "d"),
        (
            "Quick",
            (("brown", "fox"), ("jumped", (("over",),)), "a"),
            ("lazy",),
            "dog",
        ),
    ]
    counts = [0, 0, 0, 1, 6]

    def count_lists(tree: Node) -> int:
        global count
        count = 0
        psll.macros.tree_traversal(tree, pre_fun=counter)
        return count

    paired_test(subtests, trees, counts, count_lists)


def test_tree_traveral_post_fun(subtests: Subtests) -> None:
    """> Test that the list function is applied a correct number of times"""
    trees = [
        ("a",),
        ("a", "b"),
        ("a", "b", "c"),
        ("a", ("b", "c"), "d"),
        (
            "Quick",
            (("brown", "fox"), ("jumped", (("over",),)), "a"),
            ("lazy",),
            "dog",
        ),
    ]
    counts = [0, 0, 0, 1, 6]

    def count_lists(tree: Node) -> int:
        global count
        count = 0
        psll.macros.tree_traversal(tree, post_fun=counter)
        return count

    paired_test(subtests, trees, counts, count_lists)


def test_tree_traveral_post_is_post(subtests: Subtests) -> None:
    trees = [
        ("a",),
        ("a", "b"),
        ("a", "b", "c"),
        ("a", ("b", "c"), "d"),
        (
            "Quick",
            (("brown", "fox"), ("jumped", (("over",),)), "a"),
            ("lazy",),
            "dog",
        ),
    ]

    def empty_checker(node: tuple[Node]) -> Node:
        for subnode in node:
            if isinstance(subnode, str):
                assert subnode == ""
        return node

    fun = partial(psll.macros.tree_traversal, post_fun=empty_checker, str_fun=lambda x: "")
    single_test(subtests, trees, fun)


def test_tree_traveral_pre_is_pre(subtests: Subtests) -> None:
    trees = [
        ("a",),
        ("a", "b"),
        ("a", "b", "c"),
        ("a", ("b", "c"), "d"),
        (
            "Quick",
            (("brown", "fox"), ("jumped", (("over",),)), "a"),
            ("lazy",),
            "dog",
        ),
    ]

    def non_empty_checker(node: tuple[Node]) -> Node:
        for subnode in node:
            if isinstance(subnode, str):
                assert subnode != ""
        return node

    fun = partial(
        psll.macros.tree_traversal,
        pre_fun=non_empty_checker,
        str_fun=lambda x: "",
    )
    single_test(subtests, trees, fun)


final_tree: Node = None


def test_tree_traveral_final_fun(subtests: Subtests) -> None:
    trees: list[Node] = [
        ("a",),
        ("a", "b"),
        ("a", "b", "c"),
        ("a", ("b", "c"), "d"),
        (
            "Quick",
            (("brown", "fox"), ("jumped", (("over",),)), "a"),
            ("lazy",),
            "dog",
        ),
    ]
    targets: list[Node] = [
        ("",),
        ("", ""),
        ("", "", ""),
        ("", ("", ""), ""),
        ("", (("", ""), ("", (("",),)), ""), ("",), ""),
    ]

    def empty_trees(tree: Node) -> Node:
        global final_tree

        def final_look(tree: Node) -> Node:
            global final_tree
            final_tree = tree  # Pull final_tree out with the global scope
            return tree

        psll.macros.tree_traversal(tree, str_fun=lambda x: "", final_fun=final_look)
        return final_tree

    paired_test(subtests, trees, targets, empty_trees)


def test_tree_traveral_type_error(subtests: Subtests) -> None:
    """> All elements of the tree must be strings or other trees"""
    trees = [
        (1, "int"),
        (set(), "set"),
        ({}, "dict"),
        ([], "list"),
        (
            "Quick",
            (("brown", "fox"), ("jumped", (["over"],)), "a"),
            ("lazy",),
            "dog",
        ),
    ]
    error_test(subtests, trees, psll.macros.tree_traversal, TypeError)  # type: ignore


# =====================================================================================================
#
#  #####   #####    #####            #####   #####     #####    ####
#  ##  ##  ##  ##   ##               ##  ##  ##  ##   ##   ##  ##
#  #####   #####    #####  ########  #####   #####    ##   ##  ##
#  ##      ##  ##   ##               ##      ##  ##   ##   ##  ##
#  ##      ##   ##  #####            ##      ##   ##   #####    ####
#
# =====================================================================================================


def test_array_expansion_empty(subtests: Subtests) -> None:
    """> Empty array literals"""
    strings = [("set", "a", x) for x in ["[]", "[ ]", "[   ]"]]
    targets = [("set", "a", ("-", ("0", "0"), ("0", "0")))] * len(strings)
    paired_test(subtests, strings, targets, psll.macros.expand_array_literals)


def test_array_expansion_single_char(subtests: Subtests) -> None:
    """> Array literals with one element"""
    strings = [("set", "a", x) for x in ["[1]", "[1 ]", "[ 1]", "[ 1 ]"]]
    targets = [("set", "a", ("-", ("1", "0"), ("0", "0")))] * len(strings)
    paired_test(subtests, strings, targets, psll.macros.expand_array_literals)
    strings = [("set", "a", x) for x in ["[0]", "[0 ]", "[ 0]", "[ 0 ]"]]
    targets = [("set", "a", ("-", ("0", "1"), ("1", "1")))] * len(strings)
    paired_test(subtests, strings, targets, psll.macros.expand_array_literals)


def test_array_expansion_more_elements(subtests: Subtests) -> None:
    """> Actually useful arrays"""
    strings = [("set", "a", x) for x in ["[1 2]", "[1 2 3]", "[1 2 3 4]", "[1 2 3 4 5]"]]
    targets = [
        ("set", "a", ("1", "2")),
        ("set", "a", ("+", ("1", "2"), ("-", ("3", "0"), ("0", "0")))),
        ("set", "a", ("+", ("1", "2"), ("3", "4"))),
        (
            "set",
            "a",
            ("+", ("1", "2"), ("+", ("3", "4"), ("-", ("5", "0"), ("0", "0")))),
        ),
    ]
    paired_test(subtests, strings, targets, psll.macros.expand_array_literals)


def test_array_expansion_last_zero(subtests: Subtests) -> None:
    """> Make sure last zero in odd-length arrays also works"""
    strings = [("set", "a", x) for x in ["[1 2 0]", "[1 2 3 4 0]"]]
    targets = [
        ("set", "a", ("+", ("1", "2"), ("-", ("0", "1"), ("1", "1")))),
        (
            "set",
            "a",
            ("+", ("1", "2"), ("+", ("3", "4"), ("-", ("0", "1"), ("1", "1")))),
        ),
    ]
    paired_test(subtests, strings, targets, psll.macros.expand_array_literals)


def test_array_expansion_delimiters(subtests: Subtests) -> None:
    """> Different delimiter patterns"""
    strings = [("set", "a", x) for x in ["[1 2]", "[1  2]", "[ 1 2 ]", "[    1      2  ]"]]
    targets = [("set", "a", ("1", "2"))] * len(strings)
    paired_test(subtests, strings, targets, psll.macros.expand_array_literals)


def test_array_expansion_strings(subtests: Subtests) -> None:
    """> Make sure psll strings are not expanded"""
    strings = [("set", "a", x) for x in ['["hellos"]', '["hi" "sup"]', '["13" angry men]']]
    targets = [
        ("set", "a", ("-", ('"hellos"', "0"), ("0", "0"))),
        ("set", "a", ('"hi"', '"sup"')),
        ("set", "a", ("+", ('"13"', "angry"), ("-", ("men", "0"), ("0", "0")))),
    ]
    paired_test(subtests, strings, targets, psll.macros.expand_array_literals)


def test_string_expansion_string_expansion(subtests: Subtests) -> None:
    """> Make sure the prompt is expanded"""
    prompts = (random_string(N + 1) for N in range(10))
    for prompt in prompts:
        with subtests.test(prompt=prompt):
            ast = (f'"{prompt}"',)
            est = psll.macros.expand_string_literals(ast)
            assert depth(est) > depth(ast)


def test_string_expansion_empty() -> None:
    """> Empty string expands to 'eps'"""
    ast = ('""',)
    target = (("eps",),)
    assert psll.macros.expand_string_literals(ast) == target


def test_string_expansion_single_char(subtests: Subtests) -> None:
    """> Expand single character string"""
    trees = [(f'"{c}"',) for c in ascii_letters]
    targets = [(("chr", "_", f"{ord(c)!s}"),) for c in ascii_letters]
    paired_test(subtests, trees, targets, psll.macros.expand_string_literals)


def test_string_expansion_double_quote() -> None:
    """> Make sure the " sign is *not* is expanded when escaped"""
    ast = ('\\"',)
    est = psll.macros.expand_string_literals(ast)
    assert ast == est


def test_string_expansion_quote_combinations(subtests: Subtests) -> None:
    """> Expand some more strings as subtrees"""
    trees = [
        ('"hi"',),
        ("out", '"hi"'),
        ('"one"', '"two"'),
        ("set", "a", '"hello"'),
        ("set", '"a"', "hello"),
        ('"set"', "a", "hello"),
    ]
    for ast in trees:
        with subtests.test(ast=ast):
            est = psll.macros.expand_string_literals(ast)
            assert depth(est) > depth(ast)


def test_string_expansion_nested(subtests: Subtests) -> None:
    """> Expand strings in nested trees"""
    trees = [
        (('"hi"',),),
        (('"hi"',),),
        ("set", "a", ("+", "a", '"hi"')),
        ("set", "a", ("+", "a", '"hi"')),
    ]
    for ast in trees:
        with subtests.test(ast=ast):
            est = psll.macros.expand_string_literals(ast)
            assert depth(est) > depth(ast)


def test_bracket_expansion_1st_level(subtests: Subtests) -> None:
    """> Don't expand 1st level brackets (trees which are side-by-side)"""
    trees = [
        (("a",),),
        (("a",), ("b",)),
        (("a",), ("b",), ("c",)),
        (("a",), ("b",), ("c",), ("d",)),
    ]
    paired_test(subtests, trees, trees, psll.macros.expand_overfull_brackets)


def test_bracket_expansion_small_brackets(subtests: Subtests) -> None:
    """> Don't expand 2nd level brackets and beyond if they are less than 2 items"""
    trees = [("hi", (("a",),)), ("hello", (("a",), ("b",)))]
    paired_test(subtests, trees, trees, psll.macros.expand_overfull_brackets)


def test_bracket_expansion_large_brackets(subtests: Subtests) -> None:
    """> Expand 2nd level brackets and beyond"""
    trees = [
        ("hi", (("a",), ("b",), ("c",))),
        ("hello", (("a",), ("b",), ("c",), ("d",))),
        ("greetings", (("a",), ("b",), ("c",), ("d",), ("e",))),
    ]
    targets = [
        ("hi", ((("a",), ("b",)), ("c",))),
        ("hello", ((("a",), ("b",)), (("c",), ("d",)))),
        ("greetings", (((("a",), ("b",)), (("c",), ("d",))), ("e",))),
    ]
    paired_test(subtests, trees, targets, psll.macros.expand_overfull_brackets)


def test_bracket_expansion_syntax_error(subtests: Subtests) -> None:
    """> Throw a syntax error when the overfull bracket is not entirely filled with lists"""
    trees: list[Node] = [
        ("hello", ("a", ("b",), ("c",), ("d",))),
        ("greetings", (("a",), "b", ("c",), ("d",), ("e",))),
    ]
    error_test(subtests, trees, psll.macros.expand_overfull_brackets, psll.macros.PsllSyntaxError)


# =======================================================================
#
#  #####   ##   ##  ##  ##      ####
#  ##  ##  ##   ##  ##  ##      ##  ##
#  #####   ##   ##  ##  ##      ##  ##
#  ##  ##  ##   ##  ##  ##      ##  ##
#  #####    #####   ##  ######  ####
#
# =======================================================================


# @unittest.skip("blah")
def test_build_tree_simple(subtests: Subtests) -> None:
    """> Simple trees"""
    # trees = [('','_','_'),(' ','_','_'),('hi','_','_'),('out','a','_'),('set','a','1')]
    trees = [("",), (" ",), ("hi",), ("out", "a"), ("set", "a", "1")]
    trees = [psll.macros.fill_in_underscores((t,))[0] for t in trees]
    trees = [psll.macros.underscore_keyword(t) for t in trees]
    targets = [
        " ^ \n - ",
        "  ^  \n / \\ \n --- ",
        "   ^   \n  / \\  \n /hi \\ \n ----- ",
        "     ^   \n    / \\  \n   /out\\ \n  ^----- \n /a\\     \n ---     ",
        ("     ^     \n    / \\    \n   /set\\   \n  ^-----^  \n /a\\   /1\\ \n ---   --- "),
    ]
    fun = lambda tree: str(psll.build.build_tree(tree))
    paired_test(subtests, trees, targets, fun)


def test_build_tree_nested(subtests: Subtests) -> None:
    """> Nested trees"""
    # trees = [(' ',('sup','_','_'),'_'),('set','a',('+','1','1')),('out',('chr','32','_'),'b'),('loop',('!',('<=>','n','N'),'_'),('set','a',('+','a','1')))]  # noqa: E501
    trees = [
        (" ", ("sup",)),
        ("set", "a", ("+", "1", "1")),
        ("out", ("chr", "32"), "b"),
        ("loop", ("!", ("<=>", "n", "N")), ("set", "a", ("+", "a", "1"))),
    ]
    trees = [psll.macros.fill_in_underscores((t,))[0] for t in trees]
    trees = [psll.macros.underscore_keyword(t) for t in trees]
    targets = [
        "     ^  \n    / \\ \n   ^--- \n  / \\   \n /sup\\  \n -----  ",
        (
            "     ^       \n    / \\      \n   /set\\     \n  ^-----^    \n /a\\  "
            " /+\\   \n ---  ^---^  \n     /1\\ /1\\ \n     --- --- "
        ),
        (
            "         ^     \n        / \\    \n       /out\\   \n      ^-----^  \n"
            "     / \\   /b\\ \n    /chr\\  --- \n   ^-----      \n  / \\         "
            " \n /32 \\         \n -----         "
        ),
        (
            "           ^           \n          / \\          \n         /   \\    "
            "     \n        /loop \\        \n       ^-------^       \n      /!\\  "
            "   / \\      \n     ^---    /set\\     \n    / \\     ^-----^    \n  "
            " /<=>\\   /a\\   /+\\   \n  ^-----^  ---  ^---^  \n /n\\   /N\\    "
            " /a\\ /1\\ \n ---   ---     --- --- "
        ),
    ]
    fun = lambda tree: str(psll.build.build_tree(tree))
    paired_test(subtests, trees, targets, fun)


def test_build_tree_too_many(subtests: Subtests) -> None:
    """> Invalid number of keywords in a bracket"""
    trees = [("one", "two", "three", "four"), ("1", "2", "3", "4", "5")]
    fun = psll.build.build_tree
    error_test(subtests, trees, fun, RuntimeError)


def test_build_tree_invalid(subtests: Subtests) -> None:
    """> Invalid trees"""
    fun = psll.build.build_tree
    trees = [1, [], {}, set, ("set", "a", 1)]
    error_test(subtests, trees, fun, TypeError)
    # TODO Split this into multiple tests
    trees = [(), (("set",), "a", "1")]
    error_test(subtests, trees, fun, RuntimeError)
