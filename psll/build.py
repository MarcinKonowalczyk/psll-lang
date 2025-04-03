import operator
from functools import lru_cache, reduce, singledispatch
from typing import Union, overload

from .ascii_trees import AbstractTree, Pyramid

# ===================================================================================
#
#  #####   ##   ##  ####  ##      #####
#  ##  ##  ##   ##   ##   ##      ##  ##
#  #####   ##   ##   ##   ##      ##  ##
#  ##  ##  ##   ##   ##   ##      ##  ##
#  #####    #####   ####  ######  #####
#
# ===================================================================================

# mypy x singledispatch
# https://github.com/python/mypy/issues/8356#issuecomment-884548381


@singledispatch
def _build_tree(ast: Union[str, tuple, None]) -> Union[AbstractTree, None]:
    raise TypeError(f"Abstract syntax tree must be represented by a list (or just a string) not a {type(ast)}")


@overload
@_build_tree.register
def build_tree(ast: str) -> AbstractTree:
    return Pyramid.from_text(ast)


@overload
@_build_tree.register
def build_tree(ast: None) -> None:
    return None


@overload
@_build_tree.register
@lru_cache(maxsize=1024)
def build_tree(ast: tuple) -> AbstractTree:
    if len(ast) != 3:
        raise RuntimeError(f"Invalid structure of the abstract syntax tree. ({ast})")

    one, two, three = ast
    if not isinstance(one, str):
        raise RuntimeError(
            f"Invalid abstract syntax tree. The first element of each node must be a string, not a {type(one)}"
        )

    return build_tree(one) + (build_tree(two), build_tree(three))


def build_tree(ast: Union[str, tuple, None]) -> Union[AbstractTree, None]:
    return _build_tree(ast)


def build(ast: tuple) -> str:
    """Build the program from the abstract syntax tree"""
    program = str(reduce(operator.add, (build_tree(a) for a in ast)))
    # Remove excessive whitespace
    return "\n".join(line[1:].rstrip() for line in program.split("\n"))
