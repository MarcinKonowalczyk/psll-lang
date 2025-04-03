import unittest

from string import ascii_letters
from random import choice

from itertools import product

# Add '.' to path so running this file by itself also works
import os
import sys


from contextlib import contextmanager
from io import StringIO

sys.path.append(os.path.realpath("."))

import psll.ascii_trees as ascii_trees  # noqa: E402
from psll.ascii_trees import Pyramid, Tree  # noqa: E402


@contextmanager
def capture_output():
    old = sys.stdout
    try:
        sys.stdout = StringIO()
        yield sys.stdout
    finally:
        sys.stdout = old


random_string = lambda N: "".join(choice(ascii_letters) for _ in range(N))

# spell-checker: disable
TEST_CONTENT = [
    "",
    "!",
    "hi",
    "sup",
    "hola",
    "salut",
    "hellos",
    "regards",
    "morning!",
    "greetings",
]

TEST_PYRAMIDS = [
    " ^ \n - ",
    "  ^  \n /!\\ \n --- ",
    "   ^   \n  / \\  \n /hi \\ \n ----- ",
    "   ^   \n  / \\  \n /sup\\ \n ----- ",
    "   ^   \n  /h\\  \n /ola\\ \n ----- ",
    "    ^    \n   / \\   \n  /   \\  \n /salut\\ \n ------- ",
    "    ^    \n   / \\   \n  /hel\\  \n / los \\ \n ------- ",
    "    ^    \n   /r\\   \n  /ega\\  \n / rds \\ \n ------- ",
    "    ^    \n   /m\\   \n  /orn\\  \n /ing! \\ \n ------- ",
    "    ^    \n   /g\\   \n  /ree\\  \n /tings\\ \n ------- ",
]
# spell-checker: enable


class PyramidTests(unittest.TestCase):
    def test_creation(self):
        """> Create few pyramids"""
        for c in TEST_CONTENT:
            with self.subTest(content=c):
                _ = Pyramid.from_text(c)

    def test_default_space(self):
        """> Make sure the default space is a space"""
        self.assertEqual(ascii_trees.SPACE, " ")

    def test_output(self):
        """> Check output is what it is supposed to be"""
        for c, p in zip(TEST_CONTENT, TEST_PYRAMIDS):
            with self.subTest(content=c):
                with capture_output() as output:
                    print(Pyramid.from_text(c), end="")
                self.assertEqual(output.getvalue(), p)

    def test_min_width(self):
        """> Create a few pyramids, but now with minimum width"""
        for c, w in product(TEST_CONTENT, range(10)):
            with self.subTest(content=c, min_width=w):
                _ = Pyramid.from_text(c, min_width=w)

    def test_remove_spaces(self):
        """> Don't remove spaces from the input"""
        p = Pyramid.from_text("  ! ", remove_spaces=False)
        target = "   ^   \n  / \\  \n / ! \\ \n ----- "
        with capture_output() as output:
            print(p, end="")
        self.assertEqual(output.getvalue(), target)

    def test_content(self):
        """> Pyramid returning its own content"""
        for c in TEST_CONTENT:
            with self.subTest(content=c):
                p = Pyramid.from_text(c)
                self.assertEqual(p.content, c)

    def test_content_minus(self):
        """> Test a specific bug where a tree with just a '-' would not get expanded correctly"""
        contents = ["-", " " * 10 + "-" + " " * 10]
        for c in contents:
            with self.subTest(contents=c):
                p = Pyramid.from_text(c, remove_spaces=False)
                self.assertEqual(p.content, "-")

    def test_content_minus_expansion(self):
        """> Test a specific bug where a tree with just a '-' would not get expanded correctly"""
        p0 = Pyramid.from_text("-")
        p1 = Pyramid.from_text("long_variable_name")
        p2 = Pyramid.from_text("another_long_name")
        t = p0 + (p1, p2)
        self.assertIsInstance(t, Tree)

    def test_toPyramid(self):
        """Pyramid to Pyramid"""
        for c in TEST_CONTENT:
            with self.subTest(content=c):
                p = Pyramid.from_text(c)
                self.assertEqual(p, p.toPyramid())

    def test_toTree(self):
        """Pyramid to Tree"""
        for c in TEST_CONTENT:
            with self.subTest(content=c):
                p = Pyramid.from_text(c)
                t = p.toTree()
                self.assertIsInstance(t, Tree)
                self.assertEqual(hash(p), hash(t))

    def test_from_str(self):
        """> Make pyramids from string representation"""
        for p in TEST_PYRAMIDS:
            with self.subTest():
                self.assertEqual(str(Pyramid.from_str(p)), p)


class TreeTests(unittest.TestCase):
    def test_toPyramid(self):
        """> Tree to Pyramid"""
        for c in TEST_CONTENT:
            with self.subTest(content=c):
                t = Tree.from_text(c)
                p = t.toPyramid()
                self.assertIsInstance(p, Pyramid)
                self.assertEqual(hash(p), hash(t))

    def test_toTree(self):
        """> Tree to Tree"""
        for c in TEST_CONTENT:
            with self.subTest(content=c):
                t = Tree.from_text(c)
                self.assertEqual(t, t.toTree())

    def test_add_side_by_side(self):
        """> Basic add_side_by_side usage"""
        for c in product(TEST_CONTENT, repeat=2):
            p1, p2 = tuple(map(Pyramid.from_text, c))
            with self.subTest(contents=c):
                t = p1 + p2
                self.assertIsInstance(t, Tree)

    def test_side_by_side_options(self):
        """> Options of the add_side_by_side method"""
        for c in product(TEST_CONTENT, repeat=2):
            p1, p2 = tuple(map(Pyramid.from_text, c))
            for tight, odd in product((True, False), repeat=2):
                for min_spacing in range(10):
                    kwargs = {
                        "tight": tight,
                        "min_spacing": min_spacing,
                        "odd_spacing": odd,
                    }
                    with self.subTest(contents=c, **kwargs):
                        t = p1.toTree().add_side_by_side(p2, **kwargs)
                        self.assertIsInstance(t, Tree)
                        top_row = str(t).split("\n")[0]
                        I1 = top_row.find("^")
                        I2 = top_row.find("^", I1 + 1)
                        actual_spacing = I2 - I1 - 1
                        self.assertGreaterEqual(actual_spacing, min_spacing)
                        if odd:  # Make sure the spacing is actually odd
                            self.assertTrue((actual_spacing) % 2)

    def test_invalid_type(self):
        """> Type error is raised when attempting to add wrong types"""
        p = Pyramid.from_text("hello")
        for o in ("", 1, {}, [], ()):
            with self.subTest(other=o):
                with self.assertRaises(TypeError):
                    p + o
                    p.toTree() + o

    def test_add_one_child(self):
        """> Add one child on both left and right"""
        for c in product(TEST_CONTENT, repeat=2):
            p1, p2 = tuple(map(Pyramid.from_text, c))
            for which in ("left", "right"):
                with self.subTest(contents=c, which=which):
                    if which == "left":
                        t = p1 + (p2, None)
                    else:
                        t = p1 + (None, p2)
                    self.assertIsInstance(t, Tree)

    def test_asymmetric_children(self):
        """Test adding one child which is asymmetric"""
        p = Pyramid.from_text
        p1 = p("")  # Tiny parent
        p2 = p("set") + (p("n"), p("chr" * 100))  # Heavily asymmetric child
        for which in ("left", "right"):
            with self.subTest(which=which):
                if which == "left":
                    t = p1 + (p2, None)
                else:
                    t = p1 + (None, p2)
                self.assertIsInstance(t, Tree)

    def test_add_two_children(self):
        """> Add two children"""
        for c in product(TEST_CONTENT, repeat=3):
            p1, p2, p3 = tuple(map(Pyramid.from_text, c))
            with self.subTest(contents=c):
                t = p1 + (p2, p3)
                self.assertIsInstance(t, Tree)

    def test_cannot_expand_trees(self):
        """> Make sure only trees can get expanded"""
        p3 = Pyramid.from_text("Quick brown fox jumped over a lazy dog" * 10)
        for c in product(TEST_CONTENT, repeat=2):
            p1, p2 = tuple(map(Pyramid.from_text, c))
            with self.subTest(contents=c):
                t = p1 + (None, p2)  # Make a tree
                with self.assertRaises(RuntimeError):
                    r = t + (p3, p3)
                    self.assertIsInstance(t, Tree)
                    print("Oops:")
                    print(t)
                    print(r)


if __name__ == "__main__":
    unittest.main()
