__version__ = "0.1.2"

import sys

if sys.version_info < (3, 6):
    raise RuntimeError("Upgrade to python 3.6, or newer.")  # pragma: no cover


class PsllSyntaxError(SyntaxError):
    pass


from . import (  # noqa: F401, E402
    preprocessor,
    lexer,
    macros,
    build,
    optimisers,
)
