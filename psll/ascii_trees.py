# spell-checker: words Dunder rowlen fillvalue
from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import (
    TYPE_CHECKING,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
    final,
)

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


# from typing import final
from abc import ABC, abstractmethod
from itertools import islice, zip_longest

from more_itertools import pairwise

# ======================================================================================================================
#
#    ###    #####    ####  ######  #####      ###     ####  ######        ######  #####    #####  #####
#   ## ##   ##  ##  ##       ##    ##  ##    ## ##   ##       ##            ##    ##  ##   ##     ##
#  ##   ##  #####    ###     ##    #####    ##   ##  ##       ##            ##    #####    #####  #####
#  #######  ##  ##     ##    ##    ##  ##   #######  ##       ##            ##    ##  ##   ##     ##
#  ##   ##  #####   ####     ##    ##   ##  ##   ##   ####    ##            ##    ##   ##  #####  #####
#
# ======================================================================================================================

TOP = "^"
BOTTOM = "-"
L_SIDE = "/"
R_SIDE = "\\"
SPACE = " "


class row_tuple(NamedTuple):
    left: int
    center: str
    right: int


_T_AbstractTree = TypeVar("_T_AbstractTree", bound="AbstractTree")

_T_Dunder_Add_Other: TypeAlias = Union["AbstractTree", tuple[Optional["AbstractTree"], Optional["AbstractTree"]]]


class AbstractTree(ABC):
    """Abstract Tree class"""

    grid: list[row_tuple]
    width: int
    height: int

    @staticmethod
    def text2grid(
        text: str,
        *,
        min_width: int | None = None,
        remove_spaces: bool = False,
    ) -> list[row_tuple]:
        """Put text inside of a pyramid"""
        # N = ceil(sqrt(len(text))) # Number of pyramid levels
        if remove_spaces:
            text = text.replace(SPACE, "")
        if min_width:
            # Pad the string out such that the pyramid ends up having a correct width
            min_width = min_width // 2 * 2 + 1  # Make sure width is odd
            # Figure out by how much would the text have to be padded in a single line
            text_pad = min_width - len(text) - 2
            text_width = ((min_width - 1) // 2) ** 2  # Desired text width
            if text_pad > 0:
                l_pad = text_pad // 2
                r_pad = text_pad - (text_pad // 2)
                text = l_pad * SPACE + text + r_pad * SPACE
            text = (text_width - len(text)) * SPACE + text  # Pad out the rest

        # Ensure nice formatting of short keywords (without excessive SPACE)
        if len(text) == 2 or len(text) == 3:
            text = SPACE + text
        elif len(text) == 5:
            text = 4 * SPACE + text
        elif len(text) == 6:
            text = SPACE + text[:3] + SPACE + text[3:]
        elif len(text) == 7:
            text = text[:4] + SPACE + text[4:]
        elif len(text) == 10:
            text = 4 * SPACE + text[:5] + SPACE + text[5:]

        level = 0
        lines = [TOP]
        while text:
            level += 1
            i = 2 * level - 1
            front, text = (text[:i], text[i:])
            pad = i - len(front)
            lines.append(L_SIDE + front + pad * SPACE + R_SIDE)
        lines.append(BOTTOM * (2 * level + 1))
        grid = [row_tuple(level - j + 1, line, level - j + 1) for j, line in enumerate(lines)]
        grid[-1] = row_tuple(1, grid[-1][1], 1)  # Correct the padding of the final row
        return grid

    @staticmethod
    def grid2string(grid: Iterable[row_tuple]) -> str:
        return "\n".join([SPACE * left + row + SPACE * right for left, row, right in grid])

    @staticmethod
    def string2grid(string: str) -> list[row_tuple]:
        grid = []
        for row in string.split("\n"):
            i1, i2 = 0, len(row)
            for i, (l1, l2) in enumerate(pairwise(row)):
                if l1 == SPACE and l2 != SPACE and not i1:
                    i1 = i + 1
                if l1 != SPACE and l2 == SPACE:
                    i2 = i + 1
            grid.append(row_tuple(i1, row[i1:i2], len(row) - i2))
        return grid

    def __init__(self, grid: Iterable[row_tuple | tuple[int, str, int]]):
        """Initialise from a grid"""

        def rowlen(r: row_tuple) -> int:
            return r.left + len(r.center) + r.right

        _grid: list[row_tuple] = []
        for i, row in enumerate(grid):
            if isinstance(row, tuple):
                assert len(row) == 3, "All rows must be 3-length tuples"
                _row = row_tuple(*row)
            elif isinstance(row, row_tuple):
                _row = row
            else:
                raise TypeError("Grid must be a list of tuples (or row_tuples)")
            _grid.append(_row)

            if i == 0:
                self.width = rowlen(_row)
            else:
                assert rowlen(_row) == self.width, (
                    f"All rows must specify entries of the same length (row {i} has"
                    f" length {rowlen(_row)} while the first row has length"
                    f" {self.width})"
                )

        assert len(_grid) > 0, "Grid must not be empty"
        self.height = len(_grid)
        self.grid = _grid

    @classmethod
    def from_text(
        cls: type[_T_AbstractTree],
        text: str,
        min_width: int | None = None,
        remove_spaces: bool = False,
    ) -> _T_AbstractTree:
        """Initialise from keyword text"""
        _grid = cls.text2grid(text, min_width=min_width, remove_spaces=remove_spaces)
        return cls(_grid)

    @classmethod
    def from_str(cls: type[_T_AbstractTree], string: str) -> _T_AbstractTree:
        """Initialise from string representation"""
        _grid = cls.string2grid(string)
        return cls(_grid)

    @abstractmethod
    def toTree(self) -> Tree:
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def toPyramid(self) -> Pyramid:
        raise NotImplementedError("Abstract method")

    def __str__(self) -> str:
        return self.grid2string(self.grid)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} #{hash(self)}:\n{self!s}\n>"

    def __getitem__(self, key: int) -> row_tuple:
        return self.grid[key]

    def __setitem__(self, key: int, value: row_tuple) -> None:
        self.grid[key] = value

    def __hash__(self) -> int:
        return hash(tuple(self.grid))  # Trees hash the same if their grids are the same

    def __iter__(self) -> Iterator[row_tuple]:
        return iter(self.grid)

    @abstractmethod
    def __add__(self, other: _T_Dunder_Add_Other) -> AbstractTree:
        return NotImplemented


# ==============================================================================================
#
#  #####   ##    ##  #####      ###    ###    ###  ##  ####
#  ##  ##   ##  ##   ##  ##    ## ##   ## #  # ##  ##  ##  ##
#  #####     ####    #####    ##   ##  ##  ##  ##  ##  ##  ##
#  ##         ##     ##  ##   #######  ##      ##  ##  ##  ##
#  ##         ##     ##   ##  ##   ##  ##      ##  ##  ####
#
# ==============================================================================================


@final
class Pyramid(AbstractTree):
    """Single pyramid"""

    def __init__(self, grid: Iterable[row_tuple | tuple[int, str, int]]) -> None:
        super().__init__(grid)
        assert self[0].center == TOP, "Pyramid has an invalid top"
        for row, next_row in pairwise(self):
            assert row.left == row.right, "Not a pyramid"
            if not (row.left == 1 and next_row.left == 1):
                assert (row.left - 1) == next_row.left, "Not a pyramid"

    @property
    def content(self) -> str:
        content = "".join(row[1:-1].replace(SPACE, "") for _, row, _ in islice(self, 1, self.height - 1))
        return content.strip()

    def toTree(self) -> Tree:
        return Tree(self.grid)

    def toPyramid(self) -> Pyramid:
        return self

    def __add__(self, other: _T_Dunder_Add_Other) -> Tree:
        """Overload the + operator by passing self to Tree"""
        if isinstance(other, AbstractTree):
            return self.toTree() + other.toTree()
        elif isinstance(other, tuple) and len(other) == 2:
            return self.toTree() + other
        else:
            raise TypeError(f"unsupported operand type for +: '{type(self).__name__}' and '{type(other).__name__}'")


# =================================================================
#
#  ######  #####    #####  #####
#    ##    ##  ##   ##     ##
#    ##    #####    #####  #####
#    ##    ##  ##   ##     ##
#    ##    ##   ##  #####  #####
#
# =================================================================


@final
class Tree(AbstractTree):
    """Tree of pyramids"""

    @staticmethod
    def distance_row_iterator(left_tree: AbstractTree, right_tree: AbstractTree) -> Iterator[int]:
        """Return distance of closest approach of each pair of rows"""
        for left_row, right_row in zip(left_tree, right_tree):
            distance = left_row.right + right_row.left
            lc, rc = left_row.center[-1], right_row.center[0]
            if (lc == TOP and rc == BOTTOM) or (lc == BOTTOM and rc == TOP):
                distance -= 1
            yield distance

    def add_side_by_side(
        self,
        other: AbstractTree,
        *,
        tight: bool = True,
        min_spacing: int | None = None,
        odd_spacing: bool = False,
    ) -> Tree:
        """Add trees side-by-side"""
        # Find tightest squeeze between the pyramids
        squeeze = 0
        if tight:
            squeeze = min(self.distance_row_iterator(self, other))

        # Decrease the squeeze if required by the min_width
        _lr, _rr = self[0], other[0]
        p2p_distance = _lr.right + _rr.left - squeeze
        if min_spacing:
            squeeze -= max(min_spacing - p2p_distance, 0)
            p2p_distance = _lr.right + _rr.left - squeeze

        # Width of the squeezed pyramid
        squeezed_width = self.width + other.width - squeeze

        # Make sure spacing between the peaks is an odd
        if odd_spacing and not (p2p_distance % 2):
            squeeze -= 1
            squeezed_width += 1

        # Figure out signed overhang of one tree over the other and therefore the top padding
        if self.height > other.height:
            overhang = other.width - squeeze
            lp, rp = 0, max(-overhang, 0)
        else:
            overhang = self.width - squeeze
            lp, rp = max(-overhang, 0), 0

        # Put together self and the other row by row
        grid: list[row_tuple] = []
        row: row_tuple
        for lr, rr in zip_longest(self, other, fillvalue=None):
            if lr and rr:
                row = row_tuple(
                    left=lr.left + lp,
                    center=lr.center + (lr.right + rr.left - squeeze) * SPACE + rr.center,
                    right=rr.right + rp,
                )
            elif lr:
                row = row_tuple(
                    left=lr.left,
                    center=lr.center,
                    right=lr.right + max(overhang, 0),
                )
            elif rr:
                row = row_tuple(
                    left=max(overhang, 0) + rr.left,
                    center=rr.center,
                    right=rr.right,
                )
            grid.append(row)

        return Tree(grid)

    @staticmethod
    def child_row_iterator(
        parent: AbstractTree, child: AbstractTree
    ) -> Iterator[tuple[row_tuple | None, row_tuple | None]]:
        """Yield rows from parent and then from the child, signalling the changeover"""
        _parent, _child = iter(parent), iter(child)
        for row, next_row in pairwise(_parent):
            if next_row is not None:
                yield (row, None)
        yield (next_row, next(_child))  # Intermediate row
        for row in _child:
            yield (None, row)

    def add_one_child(self, child: AbstractTree, left: bool = True) -> Tree:
        """Add a left or right child to the tree"""
        assert isinstance(child, AbstractTree), "The child must be a Tree or a Pyramid"

        # Figure out the padding and overhang spacing
        # Last row of parent and first of the child
        parent_row, child_row = self[-1], child[0]

        parent_pad = child_row.left if left else child_row.right
        # NOTE: This changed whn updating to row_tuple parent_row.right -> parent_row.left
        overhang = (
            child_row.right - (len(parent_row.center) + parent_row.left)
            if left
            else child_row.left - (len(parent_row.center) + parent_row.right)
        )

        grid: list[row_tuple] = []
        row: row_tuple
        for p, c in self.child_row_iterator(self, child):
            if p and not c:
                row = row_tuple(
                    left=parent_pad + p.left if left else max(overhang, 0) + p.left,
                    center=p.center,
                    right=p.right + max(overhang, 0) if left else p.right + parent_pad,
                )
            elif p and c:
                row = row_tuple(
                    left=c.left if left else max(overhang, 0) + p.left,
                    center=c.center + p.center if left else p.center + c.center,
                    right=p.right + max(overhang, 0) if left else c.right,
                )
            elif not p and c:
                row = row_tuple(
                    left=c.left if left else max(-overhang, 0) + c.left,
                    center=c.center,
                    right=c.right + max(-overhang, 0) if left else c.right,
                )
            grid.append(row)
        return Tree(grid)

    def add_two_children(self, left: AbstractTree, right: AbstractTree) -> Tree:
        """Add left and right child to a tree"""

        try:  # Parent *must* be a single pyramid, even if children would fit
            parent_as_pyramid = self.toPyramid()
        except Exception:
            raise RuntimeError("Cannot expand non-singleton Trees") from None

        parent_width = len(self[-1][1]) // 2 * 2 + 1  # Make sure parent width is odd

        # Put children together with minimum width of a parent, make sure they're odd
        left, right = left.toTree(), right.toTree()
        children = left.add_side_by_side(right, min_spacing=parent_width, odd_spacing=True)
        actual_children_width = len(children[0].center) - 2

        # Try to expand oneself to accommodate the width of the children
        if (actual_children_width > parent_width) or (parent_width > len(self[-1][1])):
            parent = Tree.from_text(parent_as_pyramid.content, min_width=actual_children_width)
        else:
            parent = self

        lp, _, rp = children[0]

        grid: list[row_tuple] = []
        row: row_tuple
        for p, c in self.child_row_iterator(parent, children):
            if p and not c:
                row = row_tuple(
                    left=lp + p.left,
                    center=p.center,
                    right=p.right + rp,
                )
            elif p and c:
                row = row_tuple(
                    left=c.left,
                    center=c.center[0] + p.center + c.center[-1],
                    right=c.right,
                )
            elif not p and c:
                row = c
            grid.append(row)
        return Tree(grid)

    def toTree(self) -> Tree:
        return self

    def toPyramid(self) -> Pyramid:
        return Pyramid(self.grid)

    def __add__(self, other: _T_Dunder_Add_Other) -> Tree:
        if isinstance(other, AbstractTree):
            return self.add_side_by_side(other.toTree())
        elif isinstance(other, tuple) and len(other) == 2:
            left, right = other
            if left and right:
                return self.add_two_children(left, right)
            elif left:
                return self.add_one_child(left, left=True)
            elif right:
                return self.add_one_child(right, left=False)
            else:
                return self
        else:
            raise TypeError(f"unsupported operand type for +: '{type(self).__name__}' and '{type(other).__name__}'")


# ======================================================================
#
#  ###    ###    ###    ##  ##     ##
#  ## #  # ##   ## ##   ##  ####   ##
#  ##  ##  ##  ##   ##  ##  ##  ## ##
#  ##      ##  #######  ##  ##    ###
#  ##      ##  ##   ##  ##  ##     ##
#
# ======================================================================

# if __name__ == "__main__":
#     from itertools import product
#     p0 = Pyramid.from_text("")
#     p1 = Pyramid.from_text("set")
#     text = "Greetings traveller! Where goes thee this fine morning?" * 3
#     p2 = Pyramid.from_text(text, remove_spaces=False)
#     p3 = (p1 + p1 + p1) + p2

#     for i, j, k in product((p0, p1, p2), repeat=3):
#         print()
#         print(i + (j, k))
