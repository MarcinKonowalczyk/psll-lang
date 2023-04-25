import argparse
import os
import os.path as op
import shutil
import subprocess

import sys
import hashlib

from typing import Callable, TypeVar
from enum import Enum

from functools import partial

ArgumentError = partial(argparse.ArgumentError, None)
sys.tracebacklimit = 0

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
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Run in the verbose mode. Can be specified multiple times.",
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

    if not op.exists(args.input):
        raise ArgumentError("Input file does not exist")

    input_root, input_ext = op.splitext(args.input)
    if input_ext != ".psll":
        raise ArgumentError("Input file does not have .psll extension")

    if args.output == "":
        pass
    elif args.output == " ":
        args.output = input_root + ".pyra"

    if op.exists(args.output) and not args.force:
        answer = input(f"File {args.output} already exists. Overwrite? [y/N]")
        if answer.lower() != "y":
            args.output = None

    if args.output is not None:
        output_root, output_ext = op.splitext(args.output)
        if output_ext != ".pyra":
            raise ArgumentError("Output file does not have .pyra extension")


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
    run_parser = subparsers.add_parser(
        "run",
        help="run a pyramid scheme program",
    )

    run_parser.add_argument("input", help="Input pyramid scheme file.")

    run_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Run in the verbose mode. Can be specified multiple times.",
    )


@register_validate_options(Subcommand.RUN)
def _(args: argparse.Namespace) -> None:
    """Validate options for the run subcommand"""

    if not op.exists(args.input):
        raise ArgumentError("Input file does not exist")

    input_root, input_ext = op.splitext(args.input)
    if input_ext != ".pyra":
        raise ArgumentError("Input file does not have .pyra extension")


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

    # Add subcommands
    for subcommand in Subcommand:
        subcommand.add_subcommand(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Parse subcommand as Subcommand enum
    args.subcommand = Subcommand(args.subcommand)

    # Dispatch to subcommand-specific validation
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

    # Count lines and characters in the original source
    psll_lines, psll_chars = len(text.splitlines()), len(text)

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

    # Count lines and characters in the generated pyramid scheme program
    pyra_lines, pyra_chars = len(program.splitlines()), len(program)

    # Print the generated pyramid scheme program only in -vv mode
    if args.verbose > 1:
        print("Pyramid scheme:", program, sep="\n")

    if args.output:
        with open(args.output, "w") as f:
            f.write(program)

    if args.verbose:
        print("psll file:", psll_lines, "lines,", psll_chars, "characters")
        print("pyra file:", pyra_lines, "lines,", pyra_chars, "characters")


# https://github.com/ConorOBrien-Foxx/Pyramid-Scheme/blob/fd183d296f08e0cba8bf55da907697eaf412f6a7/pyra.rb
EXPECTED_HASH = "a2b8175e8807cf5acce35c73252994dd"


@register_subcommand(Subcommand.RUN)
def subcommand_run(args: argparse.Namespace) -> None:  # pragma: no cover
    """Main function for the command-line operation"""

    # rind ruby
    ruby = shutil.which("ruby")
    if ruby is None:
        raise RuntimeError(
            "Could not find ruby executable. Make sure ruby is installed."
        )

    if args.verbose:
        print("Ruby executable:", ruby)

    # get ruby version
    ruby_version = subprocess.check_output([ruby, "--version"]).decode("utf-8").strip()
    if args.verbose:
        print("Ruby version:", ruby_version)

    # find pyramid scheme executable
    candidates: list[str] = []

    # Check rhe current working directory for pyra.rb
    cwd_fullpath = op.abspath(os.getcwd())
    candidates.append(op.join(cwd_fullpath, "pyra.rb"))
    candidates.append(op.join(cwd_fullpath, "Pyramid-Scheme", "pyra.rb"))

    # Check the directory of this file for pyra.rb This is where it might get dropped
    # byt the installer
    this_file_fullpath = op.abspath(__file__)
    candidates.append(op.join(this_file_fullpath, "pyra.rb"))
    candidates.append(op.join(this_file_fullpath, "Pyramid-Scheme", "pyra.rb"))

    # Finally check the home directory
    home_dir = op.expanduser("~")
    if home_dir != "~":
        # home_dir got expanded aka it is known
        candidates.append(op.join(home_dir, "pyra.rb"))
        candidates.append(op.join(home_dir, "Pyramid-Scheme", "pyra.rb"))

    pyra_rb = None
    for candidate in candidates:
        if op.isfile(candidate):
            with open(candidate, "r") as f:
                file_hash = hashlib.md5(f.read().encode("utf-8")).hexdigest()
            if file_hash == EXPECTED_HASH:
                # This is the correct version of pyra.rb
                pyra_rb = candidate
                break
            else:
                if args.verbose:
                    print(
                        f"Found a pyra.rb file at {candidate} but it has the wrong hash"
                        f" ({file_hash} != {EXPECTED_HASH}). Ignoring it."
                    )

    if pyra_rb is None:
        raise RuntimeError(
            "Could not find pyra.rb. Make sure pyramid scheme is installed."
        )

    if args.verbose:
        print("pyra.rb:", pyra_rb)

    # run pyramid scheme
    if args.verbose:
        print("Running pyramid scheme...")

    subprocess.run([ruby, pyra_rb, args.input])


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
