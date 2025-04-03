"""
Optimisers work on the abstract syntax tree to improve byte count of the compiled code.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from typing_extensions import _T

import operator
from itertools import chain

from more_itertools import windowed_complete

from . import build


def greedy_optimisation(ast: tuple, verbose: bool = True, max_iter: int | None = None) -> tuple:
    """Greedily insert empty trees into the abstract syntax tree"""

    def candidates(ast: tuple) -> Generator[tuple, None, None]:
        for b, m, e in windowed_complete(ast, 2):  # Try all the pairs
            yield (*b, ("", m[0], m[1]), *e)
        for b, m, e in windowed_complete(ast, 1):  # Finally try all the single pyramids
            yield (*b, ("", m[0], None), *e)
            yield (*b, ("", None, m[0]), *e)

    iter_count = 0
    if verbose:
        print("Greedy tree optimisation")
    while True:
        iter_count += 1
        if max_iter and iter_count > max_iter:
            break

        N = len(build.build(ast))
        for candidate in candidates(ast):
            M = len(build.build(candidate))
            if M < N:
                if verbose:
                    print(f"{iter_count} | Old len: {N} | New len: {M}")
                ast = candidate
                break  # Greedily accept the new ast
        else:
            break  # Break from the while loop
    return ast


def repeat(func: Callable[[_T], _T], n: int, arg: _T) -> _T:
    """Apply a function ``n`` times to an argument"""
    if n < 0:
        raise ValueError
    if n == 0:
        return arg
    out = func(arg)
    for _ in range(n - 1):
        out = func(out)
    return out


def considerate_optimisation(
    ast: tuple,
    verbose: bool = True,
    max_iter: int | None = None,
    max_depth: int = 10,
) -> tuple:
    """Consider all the possible places to insert a tree up to ``max_depth``"""

    wrap_left = lambda node: ("", node, None)  # Wrap a node
    wrap_right = lambda node: ("", None, node)  # Wrap a node

    def candidates(ast: tuple) -> Generator[tuple, None, None]:
        for b, m, e in chain(windowed_complete(ast, 1), windowed_complete(ast, 2)):
            m = ("", m[0], m[1]) if len(m) == 2 else m[0]
            for d in range(1, max_depth):
                yield (*b, repeat(wrap_left, d, m), *e)
            for d in range(1, max_depth):
                yield (*b, repeat(wrap_right, d, m), *e)

    iter_count = 0
    if verbose:
        print("Considerate optimisation")
    while True:
        iter_count += 1
        if max_iter and iter_count > max_iter:
            break

        N = len(build.build(ast))
        lengths = ((len(build.build(c)), c) for c in candidates(ast))
        M, candidate = min(lengths, key=operator.itemgetter(0))
        if M < N:
            if verbose:
                print(f"{iter_count} | Old len: {N} | New len: {M}")
            ast = candidate
        else:
            break  # Break from the while loop
    return ast
