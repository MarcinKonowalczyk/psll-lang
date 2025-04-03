__version__ = "0.1.6.dev0"


class PsllSyntaxError(SyntaxError):
    pass


from . import (  # noqa: F401, E402
    build,
    lexer,
    macros,
    optimisers,
    preprocessor,
)
