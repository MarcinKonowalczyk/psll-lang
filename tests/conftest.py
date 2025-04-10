from typing import TYPE_CHECKING, Any, Optional, Protocol

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--ruby",
        action="store",
        help="specify the ruby executable to use for tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "ruby: specify the ruby executable to use for tests")


@pytest.fixture(scope="session")
def ruby(request: pytest.FixtureRequest) -> Optional[str]:
    """Fixture to get the ruby executable from the command line options"""
    ruby = request.config.getoption("--ruby", None)
    assert isinstance(ruby, (str, type(None))), f"Invalid ruby option: {ruby}"
    if isinstance(ruby, str):
        # we need to prepend the path with some garbage to make it not a valid
        # path. otherwise pytest gets confused.
        # https://github.com/pytest-dev/pytest/issues/13368
        ruby = ruby.lstrip("$")
    return ruby  # type: ignore


##========================================================================================================
##
##   ####  ##   ##  #####  ######  ######   ####  ######  ####
##  ##     ##   ##  ##  ##   ##    ##      ##       ##   ##
##   ###   ##   ##  #####    ##    #####    ###     ##    ###
##     ##  ##   ##  ##  ##   ##    ##         ##    ##      ##
##  ####    #####   #####    ##    ######  ####     ##   ####
##
##========================================================================================================


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
