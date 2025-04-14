from typing import TYPE_CHECKING, Any, Optional, Protocol

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--ruby",
        action="store",
        help="specify the ruby executable to use for tests",
    )
    parser.addoption(
        "--pyra",
        action="store",
        help="specify the pyra.rb to use for tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "ruby: specify the ruby executable to use for tests")
    config.addinivalue_line("markers", "pyra: specify the pyra.rb to use for tests")


@pytest.fixture(scope="session")
def ruby(request: pytest.FixtureRequest) -> Optional[str]:
    """Fixture to get the ruby executable from the command line options"""
    ruby = request.config.getoption("--ruby", None)
    assert isinstance(ruby, (str, type(None))), f"Invalid ruby option: {ruby}"
    return ruby


@pytest.fixture(scope="session")
def pyra(request: pytest.FixtureRequest) -> Optional[str]:
    """Fixture to get the pyra.rb from the command line options"""
    pyra = request.config.getoption("--pyra", None)
    assert isinstance(pyra, (str, type(None))), f"Invalid pyra option: {pyra}"
    return pyra


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
