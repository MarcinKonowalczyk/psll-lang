import unittest
import os
import sys

from functools import partial
from string import ascii_letters
import random

# from itertools import product, permutations
from contextlib import contextmanager

# Add '.' to path so running this file by itself also works
sys.path.append(os.path.realpath("."))

import psll  # noqa: E402
import psll.macros  # noqa: E402


def depth(tree):
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
            "The abstract syntax tree can contain only strings or other, smaller,"
            f" trees, not {type(tree).__name__}"
        )


random_string = lambda N: "".join(random.choice(ascii_letters) for _ in range(N))


# spell-checker: words prob
def random_tree(max_depth=10, str_prob=0.6):
    """Make up a random tree"""
    ast = [random_string(random.randrange(4))]
    for _ in range(2):
        if random.random() < str_prob or max_depth == 1:
            node = random_string(random.randrange(4))
        else:
            node = random_tree(max_depth=max_depth - 1)
        ast.append(node)
    return ast


@contextmanager
def psll_file(content, filename=None):
    """Mock a .psll file with certain content"""
    if not filename:  # Make temp filename
        filename = f"temp_{random_string(10)}.psll"
    try:
        with open(filename, "w") as f:
            f.write(content)
        yield filename
    finally:
        os.remove(filename)


class MetaTests:
    def paired_test(self, inputs, targets, fun):
        """Test input/target pairs with fun(input)==target"""
        self.assertEqual(len(inputs), len(targets))
        for i, t in zip(inputs, targets):
            with self.subTest(input=i):
                self.assertEqual(fun(i), t)

    def single_test(self, inputs, fun):
        """Test input with fun(input)"""
        for i in inputs:
            with self.subTest(input=i):
                fun(i)

    def error_test(self, inputs, fun, error):
        """Test that text throws an error"""
        for i in inputs:
            with self.subTest(input=i):
                with self.assertRaises(error):
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


class ReadFile(unittest.TestCase, MetaTests):
    @staticmethod
    def read_file(content):
        """read_file + preprocess"""
        with psll_file(content) as f:
            text = psll.preprocessor.read_file(f)
            return psll.preprocessor.preprocess(text)

    def test_empty(self):
        """> Read and parse files with empty brackets"""
        contents = ["", "()", "( )", "()()", "()()()", "(())", "() (())"]
        targets = ["", "()", "()", "() ()", "() () ()", "(())", "() (())"]
        self.paired_test(contents, targets, self.read_file)

    def test_simple(self):
        """> Read and parse files with simple contents"""
        contents = [
            "(set)",
            "(hi)",
            "(set 1)",
            "(set hi 1)",
            "(1 2 3 4)",
            "(hi) (salut)",  # spell-checker: disable-line
        ]
        self.paired_test(contents, contents, self.read_file)

    def test_comments(self):
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
        self.paired_test(contents, targets, self.read_file)

    @unittest.skip("Needs work")
    def test_single_spaces(self):
        """> Only single spaces"""
        contents = ["( )", "(  )", "(   )", "(     )"]
        targets = ["()", "()", "()", "()"]
        self.paired_test(contents, targets, self.read_file)

    @unittest.skip("Needs work")
    def test_leading_and_trailing_spaces(self):
        """> No leading or trailing whitespace"""
        contents = ["(   hi)", "(hi   )", "(hi   1)", "(   hi 1)", "(hi 1   )"]
        targets = ["(hi)", "(hi)", "(hi 1)", "(hi 1)", "(hi 1)"]
        self.paired_test(contents, targets, self.read_file)

    def test_multiline(self):
        """> Input over multiple lines"""
        contents = ["()\n()", "\n(hi)", "(\nhi)", "(hi\n)", "(hi)\n"]
        targets = ["() ()", "(hi)", "(hi)", "(hi)", "(hi)"]
        self.paired_test(contents, targets, self.read_file)


# =============================================================
#
#  ##      #####  ##    ##
#  ##      ##      ##  ##
#  ##      #####    ####
#  ##      ##      ##  ##
#  ######  #####  ##    ##
#
# =============================================================


@unittest.skip("Needs rewriting into tests of `lex`")
class Split(unittest.TestCase, MetaTests):
    def test_simple(self):
        """> Simple inputs"""
        texts = ["", "()", "() ()", "(hi)", "(out 1)", "(set a 1)"]
        targets = [(), ("()",), ("()", "()"), ("(hi)",), ("(out 1)",), ("(set a 1)",)]
        self.paired_test(texts, targets, psll.macros.split_into_lines)

    def test_nested(self):
        """> Nested inputs"""
        texts = ["(())", "(()) ()", "(((hi)))", "(() () hi)", "(() ()) (()) ()"]
        targets = [
            ("(())",),
            ("(())", "()"),
            ("(((hi)))",),
            ("(() () hi)",),
            ("(() ())", "(())", "()"),
        ]
        self.paired_test(texts, targets, psll.macros.split_into_lines)

    def test_error(self):
        """> Bracket parity and ketbra errors"""
        texts = ["(", ")", ")(", "(hi))", "((hi)", "((", "))", "((()())", "(()()))"]
        self.error_test(
            texts, psll.macros.split_into_lines, psll.macros.PsllSyntaxError
        )

    def test_simple_subtrees(self):
        """> Simple subtrees"""
        texts = ["(hi)", "(set a 1)", "(one two three four)"]
        targets = [("hi",), ("set", "a", "1"), ("one", "two", "three", "four")]
        self.paired_test(texts, targets, psll.split_into_subtrees)

    def test_nested_subtrees(self):
        """> Nested subtrees"""
        texts = ["(set a (= b 1))", "(a (b (() c)))"]
        targets = [("set", "a", ("=", "b", "1")), ("a", ("b", (("",), "c")))]
        self.paired_test(texts, targets, psll.split_into_subtrees)

    def test_blank(self):
        """> Trees with blank elements"""
        texts = ["()", "(())", "(() hi)", "(1 2)", "((hi 1) (hi 2))"]
        targets = [
            ("",),
            (("",),),
            (("",), "hi"),
            ("1", "2"),
            (("hi", "1"), ("hi", "2")),
        ]
        self.paired_test(texts, targets, psll.split_into_subtrees)

    def test_quotes(self):
        """> Don't split quotes"""
        texts = ['("hi")', '(set a "one")', '("string with spaces")']
        targets = [('"hi"',), ("set", "a", '"one"'), ('"string with spaces"',)]
        self.paired_test(texts, targets, psll.split_into_subtrees)

    @unittest.skip("Currently broken")
    def test_double_quote_command(self):
        """> Make sure " command is not broken (aka it does not start an unnecessary string)"""
        pass


# ==================================================================================================================================================
#
#  ######  #####    #####  #####        ######  #####      ###    ##   ##  #####  #####     ####    ###    ##
#    ##    ##  ##   ##     ##             ##    ##  ##    ## ##   ##   ##  ##     ##  ##   ##      ## ##   ##
#    ##    #####    #####  #####          ##    #####    ##   ##  ##   ##  #####  #####     ###   ##   ##  ##
#    ##    ##  ##   ##     ##             ##    ##  ##   #######   ## ##   ##     ##  ##      ##  #######  ##
#    ##    ##   ##  #####  #####          ##    ##   ##  ##   ##    ###    #####  ##   ##  ####   ##   ##  ######
#
# ==================================================================================================================================================


class TreeTraversal(unittest.TestCase, MetaTests):
    @staticmethod
    def counter(node):
        global count
        count += 1
        return node

    def test_string_fun(self):
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

        def count_strings(tree):
            global count
            count = 0
            psll.macros.tree_traversal(tree, str_fun=self.counter)
            return count

        self.paired_test(trees, counts, count_strings)

    def test_pre_fun(self):
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

        def count_lists(tree):
            global count
            count = 0
            psll.macros.tree_traversal(tree, pre_fun=self.counter)
            return count

        self.paired_test(trees, counts, count_lists)

    def test_post_fun(self):
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

        def count_lists(tree):
            global count
            count = 0
            psll.macros.tree_traversal(tree, post_fun=self.counter)
            return count

        self.paired_test(trees, counts, count_lists)

    def test_post_is_post(self):
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

        def empty_checker(node):
            for subnode in node:
                if isinstance(subnode, str):
                    self.assertEqual(subnode, "")
            return node

        fun = partial(
            psll.macros.tree_traversal, post_fun=empty_checker, str_fun=lambda x: ""
        )
        self.single_test(trees, fun)

    def test_pre_is_pre(self):
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

        def non_empty_checker(node):
            for subnode in node:
                if isinstance(subnode, str):
                    self.assertNotEqual(subnode, "")
            return node

        fun = partial(
            psll.macros.tree_traversal,
            pre_fun=non_empty_checker,
            str_fun=lambda x: "",
        )
        self.single_test(trees, fun)

    def test_final_fun(self):
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
        targets = [
            ("",),
            ("", ""),
            ("", "", ""),
            ("", ("", ""), ""),
            ("", (("", ""), ("", (("",),)), ""), ("",), ""),
        ]

        def empty_trees(tree):
            global final_tree

            def final_look(tree):
                global final_tree
                final_tree = tree  # Pull final_tree out with the global scope
                return tree

            psll.macros.tree_traversal(tree, str_fun=lambda x: "", final_fun=final_look)
            return final_tree

        self.paired_test(trees, targets, empty_trees)

    def test_type_error(self):
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
        self.error_test(trees, psll.macros.tree_traversal, TypeError)


# =====================================================================================================
#
#  #####   #####    #####            #####   #####     #####    ####
#  ##  ##  ##  ##   ##               ##  ##  ##  ##   ##   ##  ##
#  #####   #####    #####  ########  #####   #####    ##   ##  ##
#  ##      ##  ##   ##               ##      ##  ##   ##   ##  ##
#  ##      ##   ##  #####            ##      ##   ##   #####    ####
#
# =====================================================================================================


class ArrayExpansion(unittest.TestCase, MetaTests):
    def test_empty(self):
        """> Empty array literals"""
        strings = [("set", "a", x) for x in ["[]", "[ ]", "[   ]"]]
        targets = [("set", "a", ("-", ("0", "0"), ("0", "0")))] * len(strings)
        self.paired_test(strings, targets, psll.macros.expand_array_literals)

    def test_single_char(self):
        """> Array literals with one element"""
        strings = [("set", "a", x) for x in ["[1]", "[1 ]", "[ 1]", "[ 1 ]"]]
        targets = [("set", "a", ("-", ("1", "0"), ("0", "0")))] * len(strings)
        self.paired_test(strings, targets, psll.macros.expand_array_literals)
        strings = [("set", "a", x) for x in ["[0]", "[0 ]", "[ 0]", "[ 0 ]"]]
        targets = [("set", "a", ("-", ("0", "1"), ("1", "1")))] * len(strings)
        self.paired_test(strings, targets, psll.macros.expand_array_literals)

    def test_more_elements(self):
        """> Actually useful arrays"""
        strings = [
            ("set", "a", x) for x in ["[1 2]", "[1 2 3]", "[1 2 3 4]", "[1 2 3 4 5]"]
        ]
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
        self.paired_test(strings, targets, psll.macros.expand_array_literals)

    def test_last_zero(self):
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
        self.paired_test(strings, targets, psll.macros.expand_array_literals)

    def test_delimiters(self):
        """> Different delimiter patterns"""
        strings = [
            ("set", "a", x) for x in ["[1 2]", "[1  2]", "[ 1 2 ]", "[    1      2  ]"]
        ]
        targets = [("set", "a", ("1", "2"))] * len(strings)
        self.paired_test(strings, targets, psll.macros.expand_array_literals)

    def test_strings(self):
        """> Make sure psll strings are not expanded"""
        strings = [
            ("set", "a", x) for x in ['["hellos"]', '["hi" "sup"]', '["13" angry men]']
        ]
        targets = [
            ("set", "a", ("-", ('"hellos"', "0"), ("0", "0"))),
            ("set", "a", ('"hi"', '"sup"')),
            ("set", "a", ("+", ('"13"', "angry"), ("-", ("men", "0"), ("0", "0")))),
        ]
        self.paired_test(strings, targets, psll.macros.expand_array_literals)


class StingExpansion(unittest.TestCase, MetaTests):
    def test_string_expansion(self):
        """> Make sure the prompt is expanded"""
        prompts = (random_string(N + 1) for N in range(10))
        for prompt in prompts:
            with self.subTest(prompt=prompt):
                ast = (f'"{prompt}"',)
                est = psll.macros.expand_string_literals(ast)
                self.assertGreater(depth(est), depth(ast))

    def test_empty(self):
        """> Empty string expands to 'eps'"""
        ast = ('""',)
        target = (("eps",),)
        self.assertEqual(psll.macros.expand_string_literals(ast), target)

    def test_single_char(self):
        """> Expand single character string"""
        trees = [(f'"{c}"',) for c in ascii_letters]
        targets = [(("chr", "_", f"{str(ord(c))}"),) for c in ascii_letters]
        self.paired_test(trees, targets, psll.macros.expand_string_literals)

    def test_double_quote(self):
        """> Make sure the " sign is *not* is expanded when escaped"""
        ast = ('\\"',)
        est = psll.macros.expand_string_literals(ast)
        self.assertEqual(ast, est)

    def test_quote_combinations(self):
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
            with self.subTest(ast=ast):
                est = psll.macros.expand_string_literals(ast)
                self.assertGreater(depth(est), depth(ast))

    def test_nested(self):
        """> Expand strings in nested trees"""
        trees = [
            (('"hi"',),),
            (('"hi"',),),
            ("set", "a", ("+", "a", '"hi"')),
            ("set", "a", ("+", "a", '"hi"')),
        ]
        for ast in trees:
            with self.subTest(ast=ast):
                est = psll.macros.expand_string_literals(ast)
                self.assertGreater(depth(est), depth(ast))


class BracketExpansion(unittest.TestCase, MetaTests):
    def test_1st_level(self):
        """> Don't expand 1st level brackets (trees which are side-by-side)"""
        trees = [
            (("a",),),
            (("a",), ("b",)),
            (("a",), ("b",), ("c",)),
            (("a",), ("b",), ("c",), ("d",)),
        ]
        self.paired_test(trees, trees, psll.macros.expand_overfull_brackets)

    def test_small_brackets(self):
        """> Don't expand 2nd level brackets and beyond if they are less than 2 items"""
        trees = [("hi", (("a",),)), ("hello", (("a",), ("b",)))]
        self.paired_test(trees, trees, psll.macros.expand_overfull_brackets)

    def test_large_brackets(self):
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
        self.paired_test(trees, targets, psll.macros.expand_overfull_brackets)

    def test_syntax_error(self):
        """> Throw a syntax error when the overfull bracket is not entirely filled with lists"""
        trees = (
            ("hello", ("a", ("b",), ("c",), ("d",))),
            ("greetings", (("a",), "b", ("c",), ("d",), ("e",))),
        )
        self.error_test(
            trees, psll.macros.expand_overfull_brackets, psll.macros.PsllSyntaxError
        )


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
class BuildTree(unittest.TestCase, MetaTests):
    def test_simple(self):
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
            (
                "     ^     \n    / \\    \n   /set\\   \n  ^-----^  \n /a\\   /1\\ \n"
                " ---   --- "
            ),
        ]
        fun = lambda tree: str(psll.build.build_tree(tree))
        self.paired_test(trees, targets, fun)

    def test_nested(self):
        """> Nested trees"""
        # trees = [(' ',('sup','_','_'),'_'),('set','a',('+','1','1')),('out',('chr','32','_'),'b'),('loop',('!',('<=>','n','N'),'_'),('set','a',('+','a','1')))]
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
        self.paired_test(trees, targets, fun)

    def test_too_many(self):
        """> Invalid number of keywords in a bracket"""
        trees = [("one", "two", "three", "four"), ("1", "2", "3", "4", "5")]
        fun = psll.build.build_tree
        self.error_test(trees, fun, RuntimeError)

    def test_invalid(self):
        """> Invalid trees"""
        fun = psll.build.build_tree
        trees = [1, [], {}, set, ("set", "a", 1)]
        self.error_test(trees, fun, TypeError)
        # TODO Split this into multiple tests
        trees = [(), (("set",), "a", "1")]
        self.error_test(trees, fun, RuntimeError)


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)
