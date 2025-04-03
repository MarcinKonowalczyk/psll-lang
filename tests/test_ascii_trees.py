# Add '.' to path so running this file by itself also works
import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from itertools import product
from random import choice
from string import ascii_letters
from typing import Any, TypedDict, Union

import pytest
from conftest import Subtests

sys.path.append(os.path.realpath("."))

import psll.ascii_trees as ascii_trees
from psll.ascii_trees import Pyramid, Tree


@contextmanager
def capture_output() -> Iterator[StringIO]:
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

# ==========================================================================================================
#
#   #####   ##    ##  #####      ###    ###    ###  ##  ####
#   ##  ##   ##  ##   ##  ##    ## ##   ## #  # ##  ##  ##  ##
#   #####     ####    #####    ##   ##  ##  ##  ##  ##  ##  ##
#   ##         ##     ##  ##   #######  ##      ##  ##  ##  ##
#   ##         ##     ##   ##  ##   ##  ##      ##  ##  ####
#
# ==========================================================================================================


def test_pyramid_creation(subtests: Subtests) -> None:
    """> Create few pyramids"""
    for c in TEST_CONTENT:
        with subtests.test(content=c):
            _ = Pyramid.from_text(c)


def test_pyramid_default_space() -> None:
    """> Make sure the default space is a space"""
    assert ascii_trees.SPACE == " "


def test_pyramid_output(subtests: Subtests) -> None:
    """> Check output is what it is supposed to be"""
    for c, p in zip(TEST_CONTENT, TEST_PYRAMIDS):
        with subtests.test(content=c):
            with capture_output() as output:
                print(Pyramid.from_text(c), end="")
            assert output.getvalue() == p


def test_pyramid_min_width(subtests: Subtests) -> None:
    """> Create a few pyramids, but now with minimum width"""
    for c, w in product(TEST_CONTENT, range(10)):
        with subtests.test(content=c, min_width=w):
            _ = Pyramid.from_text(c, min_width=w)


def test_pyramid_remove_spaces() -> None:
    """> Don't remove spaces from the input"""
    p = Pyramid.from_text("  ! ", remove_spaces=False)
    target = "   ^   \n  / \\  \n / ! \\ \n ----- "
    with capture_output() as output:
        print(p, end="")
    assert output.getvalue() == target


def test_pyramid_content(subtests: Subtests) -> None:
    """> Pyramid returning its own content"""
    for c in TEST_CONTENT:
        with subtests.test(content=c):
            p = Pyramid.from_text(c)
            assert p.content == c


def test_pyramid_content_minus(subtests: Subtests) -> None:
    """> Test a specific bug where a tree with just a '-' would not get expanded correctly"""
    contents = ["-", " " * 10 + "-" + " " * 10]
    for c in contents:
        with subtests.test(content=c):
            p = Pyramid.from_text(c, remove_spaces=False)
            assert p.content == "-"


def test_pyramid_content_minus_expansion() -> None:
    """> Test a specific bug where a tree with just a '-' would not get expanded correctly"""
    p0 = Pyramid.from_text("-")
    p1 = Pyramid.from_text("long_variable_name")
    p2 = Pyramid.from_text("another_long_name")
    t = p0 + (p1, p2)
    assert isinstance(t, Tree)


def test_pyramid_toPyramid(subtests: Subtests) -> None:
    """> Pyramid to Pyramid"""
    for c in TEST_CONTENT:
        with subtests.test(content=c):
            p = Pyramid.from_text(c)
            assert p == p.toPyramid()


def test_pyramid_toTree(subtests: Subtests) -> None:
    """> Pyramid to Tree"""
    for c in TEST_CONTENT:
        with subtests.test(content=c):
            p = Pyramid.from_text(c)
            t = p.toTree()
            assert isinstance(t, Tree)
            assert hash(p) == hash(t)


def test_pyramid_from_str(subtests: Subtests) -> None:
    """> Make pyramids from string representation"""
    for p in TEST_PYRAMIDS:
        with subtests.test(pyramid=p):
            assert str(Pyramid.from_str(p)) == p


# =============================================================================
#
#   ######  #####    #####  #####
#     ##    ##  ##   ##     ##
#     ##    #####    #####  #####
#     ##    ##  ##   ##     ##
#     ##    ##   ##  #####  #####
#
# =============================================================================


def test_tree_toPyramid(subtests: Subtests) -> None:
    """> Tree to Pyramid"""
    for c in TEST_CONTENT:
        with subtests.test(content=c):
            t = Tree.from_text(c)
            p = t.toPyramid()
            assert isinstance(p, Pyramid)
            assert hash(p) == hash(t)


def test_tree_toTree(subtests: Subtests) -> None:
    """> Tree to Tree"""
    for c in TEST_CONTENT:
        with subtests.test(content=c):
            t = Tree.from_text(c)
            assert t == t.toTree()


def test_tree_add_side_by_side(subtests: Subtests) -> None:
    """> Basic add_side_by_side usage"""
    for c in product(TEST_CONTENT, repeat=2):
        p1, p2 = tuple(map(Pyramid.from_text, c))
        with subtests.test(contents=c):
            t = p1 + p2
            assert isinstance(t, Tree)


class AddSideBySideKwargs(TypedDict):
    """Type hint for the kwargs of add_side_by_side"""

    tight: bool
    min_spacing: Union[int, None]
    odd_spacing: bool


def test_tree_side_by_side_options(subtests: Subtests) -> None:
    """> Options of the add_side_by_side method"""
    for c in product(TEST_CONTENT, repeat=2):
        p1, p2 = tuple(map(Pyramid.from_text, c))
        for tight, odd in product((True, False), repeat=2):
            for min_spacing in range(10):
                kwargs: AddSideBySideKwargs = {
                    "tight": tight,
                    "min_spacing": min_spacing,
                    "odd_spacing": odd,
                }
                with subtests.test(contents=c, **kwargs):
                    t = p1.toTree().add_side_by_side(p2, **kwargs)
                    assert isinstance(t, Tree)
                    top_row = str(t).split("\n")[0]
                    I1 = top_row.find("^")
                    I2 = top_row.find("^", I1 + 1)
                    actual_spacing = I2 - I1 - 1
                    assert actual_spacing >= min_spacing
                    if odd:  # Make sure the spacing is actually odd
                        assert actual_spacing % 2 == 1


def test_tree_invalid_type(subtests: Subtests) -> None:
    """> Type error is raised when attempting to add wrong types"""
    p = Pyramid.from_text("hello")
    o: Any
    for o in ("", 1, {}, [], ()):
        with subtests.test(other=o), pytest.raises(TypeError):
            _ = p + o
            p.toTree() + o


def test_tree_add_one_child(subtests: Subtests) -> None:
    """> Add one child on both left and right"""
    for c in product(TEST_CONTENT, repeat=2):
        p1, p2 = tuple(map(Pyramid.from_text, c))
        for which in ("left", "right"):
            with subtests.test(contents=c, which=which):
                if which == "left":
                    t = p1 + (p2, None)
                else:
                    t = p1 + (None, p2)
                assert isinstance(t, Tree)


def test_tree_asymmetric_children(subtests: Subtests) -> None:
    """Test adding one child which is asymmetric"""
    p = Pyramid.from_text
    p1 = p("")  # Tiny parent
    p2 = p("set") + (p("n"), p("chr" * 100))  # Heavily asymmetric child
    for which in ("left", "right"):
        with subtests.test(which=which):
            if which == "left":
                t = p1 + (p2, None)
            else:
                t = p1 + (None, p2)
            assert isinstance(t, Tree)


def test_tree_add_two_children(subtests: Subtests) -> None:
    """> Add two children"""
    for c in product(TEST_CONTENT, repeat=3):
        p1, p2, p3 = tuple(map(Pyramid.from_text, c))
        with subtests.test(contents=c):
            t = p1 + (p2, p3)
            assert isinstance(t, Tree)


def test_tree_cannot_expand_trees(subtests: Subtests) -> None:
    """> Make sure only trees can get expanded"""
    p3 = Pyramid.from_text("Quick brown fox jumped over a lazy dog" * 10)
    for c in product(TEST_CONTENT, repeat=2):
        p1, p2 = tuple(map(Pyramid.from_text, c))
        with subtests.test(contents=c):
            t = p1 + (None, p2)  # Make a tree
            with pytest.raises(RuntimeError):
                r = t + (p3, p3)
                assert isinstance(r, Tree)
                print("Oops:")
                print(t)
                print(r)
