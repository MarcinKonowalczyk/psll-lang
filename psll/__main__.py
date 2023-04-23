import argparse
import os.path as op


from typing import Callable, TypeVar
from enum import Enum


ADD_SUBCOMMAND: dict["Subcommand", Callable] = {}
VALIDATE_OPTIONS: dict["Subcommand", Callable] = {}
RUN_SUBCOMMAND: dict["Subcommand", Callable] = {}


class Subcommand(Enum):
    """Enum for the subcommand"""

    COMPILE = "compile"
    RUN = "run"
    COMPILE_AND_RUN = "compile_and_run"

    def add_subcommand(self, subparsers: argparse._SubParsersAction) -> None:
        """Add the subcommand to the subparsers"""
        ADD_SUBCOMMAND[self](subparsers)

    def validate_options(self, args: argparse.Namespace) -> None:
        """Validate the options for this subcommand"""
        VALIDATE_OPTIONS[self](args)

    def run(self, args: argparse.Namespace) -> None:
        """Run the subcommand"""
        RUN_SUBCOMMAND[self](args)


_T_Callable = TypeVar("_T_Callable", bound=Callable)


def register_add_subcommand(subcommand: Subcommand) -> Callable:
    """Decorator to register a function as the add subcommand function"""

    def decorator(func: _T_Callable) -> _T_Callable:
        ADD_SUBCOMMAND[subcommand] = func
        return func

    return decorator


def register_validate_options(subcommand: Subcommand) -> Callable:
    """Decorator to register a function as the validate options function for a subcommand"""

    def decorator(func: _T_Callable) -> _T_Callable:
        VALIDATE_OPTIONS[subcommand] = func
        return func

    return decorator


def register_subcommand(subcommand: Subcommand) -> Callable:
    """Decorator to register a function as the subcommand function"""

    def decorator(func: _T_Callable) -> _T_Callable:
        RUN_SUBCOMMAND[subcommand] = func
        return func

    return decorator


def check_all_subcommands_registered() -> None:
    """Check that all subcommands are registered"""
    for subcommand in Subcommand:
        if subcommand not in ADD_SUBCOMMAND:
            raise RuntimeError(
                f"Subcommand {subcommand} is not registered! Missing add subcommand."
            )
        if subcommand not in VALIDATE_OPTIONS:
            raise RuntimeError(
                f"Subcommand {subcommand} is not registered! Missing validate options."
            )
        if subcommand not in RUN_SUBCOMMAND:
            raise RuntimeError(
                f"Subcommand {subcommand} is not registered! Missing run subcommand."
            )


# ==================================================================================================
#
#   #####  ####   ##    ##  #####  ####  ##      ######
#  ##     ##  ##  ###  ###  ##  ##  ##   ##      ##
#  ##     ##  ##  ## ## ##  #####   ##   ##      #####
#  ##     ##  ##  ##    ##  ##      ##   ##      ##
#   #####  ####   ##    ##  ##     ####  ######  ######
#
# ==================================================================================================

# Compiler options
# compile_parser.add_argument('-nt','--null-trees', action='store_true',
#     help='Use null (height 0) trees.')
# compile_parser.add_argument('--dot-spaces', action='store_true',
#     help='Render spaces as dots')


@register_add_subcommand(Subcommand.COMPILE)
def _(subparsers: argparse._SubParsersAction) -> None:
    """Add options to the compile subcommand parser"""

    compile_parser = subparsers.add_parser(
        "compile",
        help="compile a psll program to a pyramid scheme program",
    )

    compile_parser.add_argument(
        "input",
        help=(
            "Input file written in the pyramid scheme (lisp (like)) syntax, with the"
            " .psll expension."
        ),
    )
    compile_parser.add_argument(
        "-o",
        dest="output",
        required=False,
        metavar="output",
        nargs="?",
        default="",
        const=" ",
        help=(
            'Output pyramid scheme. If "output" is supplied, the pyramid scheme is'
            ' saved to that filename. If no "output" is supplied (aka just the -o'
            " option) the pyramid scheme is saved to the filename matching the input"
            " filename, with the .pyra extension."
        ),
    )
    compile_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Run in the verbose mode."
    )
    compile_parser.add_argument(
        "-f", "--force", action="store_true", help="Force file overwrite."
    )

    compile_parser.add_argument(
        "--full-names",
        action="store_true",
        help=(
            "Don't shorten variable names when compiling the pyramid scheme. This will"
            " result in longer, but potentially more readable source code. Usefull for"
            " either compiler or pyramid scheme debugging."
        ),
    )

    compile_parser.add_argument(
        "-go",
        "--greedy-optimisation",
        action="store_true",
        help=(
            "Greedily insert an empty pyramid the very first place which minimised the"
            " size is beneficial. This tends to result in tall source code."
        ),
    )
    compile_parser.add_argument(
        "-co",
        "--considerate-optimisation",
        action="store_true",
        help=(
            "Consider all the possible places to insert a pyramid, up to certain depth."
            " Choose the most beneficial. This tends to result in wide source code."
        ),
    )


@register_validate_options(Subcommand.COMPILE)
def _(args: argparse.Namespace) -> None:
    """Validate options for the compile subcommand"""

    def valid_input_file(filename: str) -> str:
        if not op.exists(filename):
            raise argparse.ArgumentTypeError(f"The file {filename} does not exist!")
        if op.splitext(filename)[1] != ".psll":
            raise argparse.ArgumentTypeError(
                "The input file does not have an .psll extension!"
            )
        return filename

    valid_input_file(args.input)

    if args.output == "":
        pass
    elif args.output == " ":
        args.output = op.splitext(args.input)[0] + ".pyra"

    if op.exists(args.output) and not args.force:
        answer = input(f"File {args.output} already exists. Overwrite? [y/N]")
        if answer.lower() != "y":
            args.output = None

    if args.output is not None and op.splitext(args.output)[1] != ".pyra":
        raise argparse.ArgumentTypeError(
            "The output file does not have an .pyra extension!"
        )


# ======================================================================
#
#  #####   ##   ##  ##   ##
#  ##  ##  ##   ##  ###  ##
#  #####   ##   ##  #### ##
#  ##  ##  ##   ##  ## ####
#  ##   ##  #####   ##  ###
#
# ======================================================================


@register_add_subcommand(Subcommand.RUN)
def _(subparsers: argparse._SubParsersAction) -> None:
    """Run a pyramid scheme program"""
    subparsers.add_parser(
        "run",
        help="run a pyramid scheme program",
    )


@register_validate_options(Subcommand.RUN)
def _(args: argparse.Namespace) -> None:
    """Validate options for the run subcommand"""
    raise NotImplementedError


# ==================================================================================================================================================================
#
#   #####  ####   ##    ##  #####  ####  ##      ######          ###    ##   ##  #####         #####   ##   ##  ##   ##
#  ##     ##  ##  ###  ###  ##  ##  ##   ##      ##             ## ##   ###  ##  ##  ##        ##  ##  ##   ##  ###  ##
#  ##     ##  ##  ## ## ##  #####   ##   ##      #####         ##   ##  #### ##  ##  ##        #####   ##   ##  #### ##
#  ##     ##  ##  ##    ##  ##      ##   ##      ##            #######  ## ####  ##  ##        ##  ##  ##   ##  ## ####
#   #####  ####   ##    ##  ##     ####  ######  ######        ##   ##  ##  ###  #####         ##   ##  #####   ##  ###
#
# ==================================================================================================================================================================


@register_add_subcommand(Subcommand.COMPILE_AND_RUN)
def _(subparsers: argparse._SubParsersAction) -> None:
    """Compile and run a psll program"""
    subparsers.add_parser(
        "compile-and-run",
        help="compile and run a psll program",
    )


@register_validate_options(Subcommand.COMPILE_AND_RUN)
def _(args: argparse.Namespace) -> None:
    """Validate options for the compile-and-run subcommand"""
    raise NotImplementedError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile lisp-like syntax to Pyramid Scheme",
    )

    subparsers = parser.add_subparsers(
        required=True,
        dest="subcommand",
    )

    for subcommand in Subcommand:
        subcommand.add_subcommand(subparsers)

    args = parser.parse_args()

    # Parser subcommand as Subcommand enum
    args.subcommand = Subcommand(args.subcommand)

    args.subcommand.validate_options(args)

    return args


# ======================================================================
#
#  ###    ###    ###    ##  ##     ##
#  ## #  # ##   ## ##   ##  ####   ##
#  ##  ##  ##  ##   ##  ##  ##  ## ##
#  ##      ##  #######  ##  ##    ###
#  ##      ##  ##   ##  ##  ##     ##
#
# ======================================================================

from . import (  # noqa: E402
    preprocessor,
    lexer,
    macros,
    build,
    optimisers,
)


@register_subcommand(Subcommand.COMPILE)
def subcommand_compile(args: argparse.Namespace) -> None:  # pragma: no cover
    """Main function for the command-line operation"""
    if args.verbose:
        print("Input filename:", args.input)
    if args.output and args.verbose:
        print("Output filename:", args.output)

    text = preprocessor.read_file(args.input)

    text = preprocessor.preprocess(text)
    if args.verbose:
        print("Reduced source:", text)

    ast = lexer.lex(text)
    # print(ast, end="\n\n")
    # names = find_variable_names(ast)
    # print('variables:',variables)

    ast = macros.apply_processing_stack(ast, full_names=args.full_names)
    # print(ast)
    # TODO  Make optimisation options mutually exclusive
    if args.considerate_optimisation:
        ast = optimisers.considerate_optimisation(ast, max_iter=None)
    if args.greedy_optimisation:
        ast = optimisers.greedy_optimisation(ast, max_iter=None)

    program = build.build(ast)
    if args.verbose:
        print("Pyramid scheme:", program, sep="\n")

    if args.output:
        with open(args.output, "w") as f:
            f.write(program)


@register_subcommand(Subcommand.RUN)
def subcommand_run(args: argparse.Namespace) -> None:  # pragma: no cover
    """Main function for the command-line operation"""
    raise NotImplementedError("Running pyramid scheme programs is not yet implemented.")


@register_subcommand(Subcommand.COMPILE_AND_RUN)
def subcommand_compile_and_run(args: argparse.Namespace) -> None:  # pragma: no cover
    """Main function for the command-line operation"""
    raise NotImplementedError(
        "Compiling and running pyramid scheme programs is not yet implemented."
    )


check_all_subcommands_registered()


# Called as a script
def argparse_and_main() -> None:  # pragma: no cover
    args = parse_args()
    args.subcommand.run(args)


# Called as a module
if __name__ == "__main__":  # pragma: no cover
    argparse_and_main()
