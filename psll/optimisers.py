"""
Optimisers work on the abstract syntax tree to improve byte count of the compiled code.
"""

from typing import Optional

from itertools import chain
from more_itertools import windowed_complete
import operator

from . import compiler

def greedy_optimisation(ast, verbose: bool = True, max_iter: Optional[int] = None):
    """Greedily insert empty trees into the abstract syntax tree"""

    def candidates(ast):
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

        N = len(compiler.compile(ast))
        for candidate in candidates(ast):
            M = len(compiler.compile(candidate))
            if M < N:
                if verbose:
                    print(f"{iter_count} | Old len: {N} | New len: {M}")
                ast = candidate
                break  # Greedilly accept the new ast
        else:
            break  # Break from the while loop
    return ast


def repeat(func, n, arg):
    if n < 0:
        raise ValueError
    if n == 0:
        return arg
    out = func(arg)
    for _ in range(n - 1):
        out = func(out)
    return out


def considerate_optimisation(ast, verbose=True, max_iter=None, max_depth=10):
    """Consider all the possible places to insert a tree up to ``max_depth``"""

    wrap_left = lambda node: ("", node, None)  # Wrap a node
    wrap_right = lambda node: ("", None, node)  # Wrap a node

    def candidates(ast):
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

        N = len(compiler.compile(ast))
        lengths = ((len(compiler.compile(c)), c) for c in candidates(ast))
        M, candidate = min(lengths, key=operator.itemgetter(0))
        if M < N:
            if verbose:
                print(f"{iter_count} | Old len: {N} | New len: {M}")
            ast = candidate
        else:
            break  # Break from the while loop
    return ast
