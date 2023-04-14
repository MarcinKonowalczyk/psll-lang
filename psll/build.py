from typing import overload, Union
from functools import lru_cache, singledispatch, reduce
import operator

from .ascii_trees import Pyramid, AbstractTree

# ===================================================================================
#
#  #####   ##   ##  ####  ##      #####
#  ##  ##  ##   ##   ##   ##      ##  ##
#  #####   ##   ##   ##   ##      ##  ##
#  ##  ##  ##   ##   ##   ##      ##  ##
#  #####    #####   ####  ######  #####
#
# ===================================================================================


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


def build(ast) -> str:
    """Build the program from the abstract syntax tree"""
    program = str(reduce(operator.add, (build_tree(a) for a in ast)))
    # Remove excessive whitespace
    return "\n".join(line[1:].rstrip() for line in program.split("\n"))
