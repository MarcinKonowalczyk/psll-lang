# Add '.' to path so running this file by itself also works
import os
import sys
from itertools import product

sys.path.append(os.path.realpath("."))

# import ascii_trees
import perf_helpers as perf

from psll.ascii_trees import Pyramid, Tree

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
# spell-checker: enable


def perf_pyramid_from_text() -> perf.stats_result:
    f = lambda: [Pyramid.from_text(c) for c in TEST_CONTENT]
    T = perf.runtime(f, divisor=len(TEST_CONTENT))
    return perf.stats(T)


def perf_tree_from_text() -> perf.stats_result:
    f = lambda: [Tree.from_text(c) for c in TEST_CONTENT]
    T = perf.runtime(f, divisor=len(TEST_CONTENT))
    return perf.stats(T)


def perf_add_side_by_side() -> perf.stats_result:
    """Test performance of adding pyramids side by side"""
    pyramids = []
    for c in product(TEST_CONTENT, repeat=2):
        p1, p2 = tuple(map(Pyramid.from_text, c))
        pyramids.append((p1, p2))

    def f() -> None:
        for p1, p2 in pyramids:
            _ = p1 + p2

    T = perf.runtime(f, 1.0, divisor=len(pyramids))
    # T = perf.ncalls(f, 1000, divisor=len(pyramids))
    return perf.stats(T)


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) == 2:
        with open(argv[1], "w") as of:
            of.write("benchmark_name center spread_upper spread_lower N\n")
            loc = dict(locals())
            for name, fun in loc.items():
                if callable(fun) and name.startswith("perf_"):
                    result = fun()
                    result = [int(t * 1e9) for t in result[:-1]] + [result[-1]]
                    of.write(f"{name} " + " ".join(f"{x:.0f}" for x in result) + "\n")
    else:
        print("running performance analysis")
        print("center, spread_upper, spread_lower, n_calls")
        print("time in ns\n---")
        loc = dict(locals())
        for name, fun in loc.items():
            if callable(fun) and name.startswith("perf_"):
                result = fun()
                result = [int(t * 1e9) for t in result[:-1]] + [result[-1]]
                print(f"{name:<30} " + " ".join(f"{x:<10.0f}" for x in result))
