"""
Macro-driven metalanguage which compiles to Pyramid Scheme.
"""

__version__ = "0.1.8"


class PsllSyntaxError(SyntaxError):
    pass


from . import (  # noqa: F401, E402
    build,
    lexer,
    macros,
    optimisers,
    preprocessor,
)
