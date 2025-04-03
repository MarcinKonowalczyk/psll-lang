"""
Macro-driven metalanguage which compiles to [Pyramid Scheme](https://github.com/ConorOBrien-Foxx/Pyramid-Scheme).
"""

__version__ = "0.1.7"


class PsllSyntaxError(SyntaxError):
    pass


from . import (  # noqa: F401, E402
    build,
    lexer,
    macros,
    optimisers,
    preprocessor,
)
