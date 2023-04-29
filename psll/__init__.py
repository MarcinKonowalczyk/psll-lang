__version__ = "0.1.5"

import sys

if sys.version_info < (3, 9):
    raise RuntimeError("Upgrade to python 3.9, or newer.")  # pragma: no cover


class PsllSyntaxError(SyntaxError):
    pass


from . import (  # noqa: F401, E402
    preprocessor,
    lexer,
    macros,
    build,
    optimisers,
)
