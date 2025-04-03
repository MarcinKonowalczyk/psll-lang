# import pytest_subtests


# def pytest_addoption(parser: pytest.Parser) -> None:
#     group = parser.getgroup("subtests")
#     group.addoption(
#         "--no-subtests-shortletter",
#         action="store_true",
#         dest="no_subtests_shortletter",
#         default=False,
#         help="Disables subtest output 'dots' in non-verbose mode (EXPERIMENTAL)",
#     )


##========================================================================================================
##
##   ####  ##   ##  #####  ######  ######   ####  ######  ####
##  ##     ##   ##  ##  ##   ##    ##      ##       ##   ##
##   ###   ##   ##  #####    ##    #####    ###     ##    ###
##     ##  ##   ##  ##  ##   ##    ##         ##    ##      ##
##  ####    #####   #####    ##    ######  ####     ##   ####
##
##========================================================================================================

from typing import TYPE_CHECKING, Any, Protocol


class Subtests(Protocol):
    def test(self, **kwargs: Any) -> "Subtests": ...

    def __enter__(self) -> "Subtests": ...

    def __exit__(self, *args: Any) -> None: ...


class NullSubtests:
    def test(self, **kwargs: Any) -> "NullSubtests":
        return self

    def __enter__(self) -> "NullSubtests":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


if TYPE_CHECKING:
    _null_subtests: Subtests = NullSubtests.__new__(NullSubtests)
