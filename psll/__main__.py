import argparse
import hashlib
import os
import os.path as op
import shutil
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = Any

from enum import Enum
from functools import partial

from . import __version__

ArgumentError = partial(argparse.ArgumentError, None)
sys.tracebacklimit = 0  # spell-checker: disable-line

Add_Sig: TypeAlias = Callable[[argparse._SubParsersAction], None]
Validate_Sig: TypeAlias = Callable[[argparse.Namespace, list[str]], tuple[argparse.Namespace, list[str]]]
Run_Sig: TypeAlias = Callable[[argparse.Namespace, list[str]], None]

ADD_SUBCOMMAND: dict["Subcommand", Add_Sig] = {}
VALIDATE_OPTIONS: dict["Subcommand", Validate_Sig] = {}
RUN_SUBCOMMAND: dict["Subcommand", Run_Sig] = {}


class Subcommand(Enum):
    """Enum for the subcommand"""

    COMPILE = "compile"
    RUN = "run"
    COMPILE_AND_RUN = "compile-and-run"
    DOWNLOAD_PYRA = "download-pyra"

    def add_subcommand(self, subparsers: argparse._SubParsersAction) -> None:
        """Add the subcommand to the subparsers"""
        ADD_SUBCOMMAND[self](subparsers)

    def validate_options(self, args: argparse.Namespace, extra: list[str]) -> tuple[argparse.Namespace, list[str]]:
        """Validate the options for this subcommand"""
        return VALIDATE_OPTIONS[self](args, extra)

    def run(self, args: argparse.Namespace, extra: list[str]) -> None:
        """Run the subcommand"""
        RUN_SUBCOMMAND[self](args, extra)


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
            raise RuntimeError(f"Subcommand {subcommand} is not registered! Missing add subcommand.")
        if subcommand not in VALIDATE_OPTIONS:
            raise RuntimeError(f"Subcommand {subcommand} is not registered! Missing validate options.")
        if subcommand not in RUN_SUBCOMMAND:
            raise RuntimeError(f"Subcommand {subcommand} is not registered! Missing run subcommand.")


# ==================================================================================================
#
#   #####  ####   ##    ##  #####  ####  ##      ######
#  ##     ##  ##  ###  ###  ##  ##  ##   ##      ##
#  ##     ##  ##  ## ## ##  #####   ##   ##      #####
#  ##     ##  ##  ##    ##  ##      ##   ##      ##
#   #####  ####   ##    ##  ##     ####  ######  ######
#
# ==================================================================================================


@register_add_subcommand(Subcommand.COMPILE)
def _(subparsers: argparse._SubParsersAction) -> None:
    """Add options to the compile subcommand parser"""

    compile_parser = subparsers.add_parser(
        "compile",
        help="compile a psll program to a pyramid scheme program",
    )

    compile_parser.add_argument(
        "input",
        help=("Input file written in the pyramid scheme (lisp (like)) syntax, with the .psll expansion."),
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

    compile_parser.add_argument("-f", "--force", action="store_true", help="Force file overwrite.")

    compile_parser.add_argument(
        "--full-names",
        action="store_true",
        help=(
            "Don't shorten variable names when compiling the pyramid scheme. This will"
            " result in longer, but potentially more readable source code. Useful for"
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


# Compiler options
# compile_parser.add_argument('-nt','--null-trees', action='store_true',
#     help='Use null (height 0) trees.')
# compile_parser.add_argument('--dot-spaces', action='store_true',
#     help='Render spaces as dots')


@register_validate_options(Subcommand.COMPILE)
def _(args: argparse.Namespace, extra: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Validate options for the compile subcommand"""

    if len(extra) != 0:
        raise ArgumentError(f"Unknown arguments: {extra}")

    if not op.exists(args.input):
        raise ArgumentError("Input file does not exist")

    args.input = op.abspath(args.input)

    input_root, input_ext = op.splitext(args.input)
    if input_ext != ".psll":
        raise ArgumentError("Input file does not have .psll extension")

    if args.output == "":
        pass
    elif args.output == " ":
        args.output = input_root + ".pyra"

    if op.exists(args.output) and not args.force:
        args.output = op.abspath(args.output)
        answer = input(f"File {args.output} already exists. Overwrite? [y/N]")
        if answer.lower() != "y":
            # Silently exit, but with error code so that it can be used in scripts
            sys.exit(1)

    if args.output is not None and args.output != "":
        output_root, output_ext = op.splitext(args.output)
        if output_ext != ".pyra":
            raise ArgumentError("Output file does not have .pyra extension")

    return args, extra


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


@register_validate_options(Subcommand.RUN)
def _(args: argparse.Namespace, extra: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Validate options for the run subcommand"""

    if not op.exists(args.input):
        raise ArgumentError("Input file does not exist")

    input_root, input_ext = op.splitext(args.input)
    if input_ext != ".pyra":
        raise ArgumentError("Input file does not have .pyra extension")

    return args, extra


# ======================================================================================================================
#
#   #####  ####   ##    ##  #####  ####  ##      ######          ###    ##   ##  #####         #####   ##   ##  ##   ##
#  ##     ##  ##  ###  ###  ##  ##  ##   ##      ##             ## ##   ###  ##  ##  ##        ##  ##  ##   ##  ###  ##
#  ##     ##  ##  ## ## ##  #####   ##   ##      #####         ##   ##  #### ##  ##  ##        #####   ##   ##  #### ##
#  ##     ##  ##  ##    ##  ##      ##   ##      ##            #######  ## ####  ##  ##        ##  ##  ##   ##  ## ####
#   #####  ####   ##    ##  ##     ####  ######  ######        ##   ##  ##  ###  #####         ##   ##  #####   ##  ###
#
# ======================================================================================================================


@register_add_subcommand(Subcommand.COMPILE_AND_RUN)
def _(subparsers: argparse._SubParsersAction) -> None:
    """Compile and run a psll program"""
    compile_and_run_parser = subparsers.add_parser(
        "compile-and-run",
        help="compile and run a psll program",
    )

    compile_and_run_parser.add_argument(
        "input",
        help=("Input file written in the pyramid scheme (lisp (like)) syntax, with the .psll extension."),
    )


@register_validate_options(Subcommand.COMPILE_AND_RUN)
def _(args: argparse.Namespace, extra: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Validate options for the compile-and-run subcommand"""
    # No validation needed. Will be validated by the compile and run subcommands

    if not op.exists(args.input):
        raise ArgumentError("Input file does not exist")

    args.input = op.abspath(args.input)

    input_root, input_ext = op.splitext(args.input)
    if input_ext != ".psll":
        raise ArgumentError("Input file does not have .psll extension")

    return args, extra


# ===============================================================================================================
#
#  #####    ####   ##    ##  ##   ##  ##      ####     ###    #####
#  ##  ##  ##  ##  ##    ##  ###  ##  ##     ##  ##   ## ##   ##  ##
#  ##  ##  ##  ##  ## ## ##  #### ##  ##     ##  ##  ##   ##  ##  ##
#  ##  ##  ##  ##  ###  ###  ## ####  ##     ##  ##  #######  ##  ##
#  #####    ####   ##    ##  ##  ###  ######  ####   ##   ##  #####
#
# ===============================================================================================================


@register_add_subcommand(Subcommand.DOWNLOAD_PYRA)
def _(subparsers: argparse._SubParsersAction) -> None:
    """Compile and run a psll program"""
    download_command = subparsers.add_parser(
        "download-pyra",
        help="download the pyramid scheme interpreter",
    )

    group = download_command.add_mutually_exclusive_group()

    group.add_argument(
        "--here",
        action="store_true",
        help="Download the interpreter in the current directory",
        default=False,
    )

    group.add_argument(
        "--home",
        action="store_true",
        help="Download the interpreter in the home directory",
        default=False,
    )

    group.add_argument(
        "-d",
        "--directory",
        help="Download the interpreter in the specified directory",
        type=str,
        default=None,
    )

    download_command.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force overwrite of the interpreter if it already exists",
        default=False,
    )


@register_validate_options(Subcommand.DOWNLOAD_PYRA)
def _(args: argparse.Namespace, extra: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Validate options for the download-pyra subcommand"""

    if len(extra) != 0:
        raise ArgumentError(f"Unknown arguments: {extra}")

    return args, extra


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Compile lisp-like syntax to Pyramid Scheme",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Run in the verbose mode. Can be specified multiple times.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"psll {__version__}",
    )

    subparsers = parser.add_subparsers(
        required=True,
        dest="subcommand",
    )

    # Add subcommands
    for subcommand in Subcommand:
        subcommand.add_subcommand(subparsers)

    # Parse arguments
    args, extra = parser.parse_known_args()

    # Parse subcommand as Subcommand enum
    args.subcommand = Subcommand(args.subcommand)

    # Dispatch to subcommand-specific validation
    return args.subcommand.validate_options(args, extra)


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
    build,
    lexer,
    macros,
    optimisers,
    preprocessor,
)


@register_subcommand(Subcommand.COMPILE)
def _(args: argparse.Namespace, extra: list[str]) -> None:
    """Main function for the command-line operation"""

    if args.verbose:
        just_filename = op.basename(args.input)
        print(f"Compiling {just_filename} to pyramid scheme")

    if args.verbose > 1:
        print("Input filename:", args.input)

    if args.output and args.verbose > 1:
        print("Output filename:", args.output)

    text = preprocessor.read_file(args.input)

    # Count lines and characters in the original source
    psll_lines, psll_chars = len(text.splitlines()), len(text)

    text = preprocessor.preprocess(text)
    if args.verbose > 2:
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
    if args.verbose > 2:
        print("Pyramid scheme:", program, sep="\n")

    if args.output:
        with open(args.output, "w") as f:
            f.write(program)

    if args.verbose:
        print("psll file:", psll_lines, "lines,", psll_chars, "characters")
        print("pyra file:", pyra_lines, "lines,", pyra_chars, "characters")


# PYRA_RB_URL = "https://raw.github.com/ConorOBrien-Foxx/Pyramid-Scheme/blob/fd183d296f08e0cba8bf55da907697eaf412f6a7/pyra.rb"
PYRA_RB_URL = (
    "https://raw.githubusercontent.com/ConorOBrien-Foxx/Pyramid-Scheme/fd183d296f08e0cba8bf55da907697eaf412f6a7/pyra.rb"
)
EXPECTED_HASH = "a2b8175e8807cf5acce35c73252994dd"


def find_pyra_rb(verbose: int) -> Optional[str]:
    """Find the pyramid scheme interpreter"""
    candidates: list[str] = []

    # Check rhe current working directory for pyra.rb
    cwd_fullpath = op.abspath(os.getcwd())
    candidates.append(op.join(cwd_fullpath, "pyra.rb"))
    candidates.append(op.join(cwd_fullpath, "Pyramid-Scheme", "pyra.rb"))

    # Check the directory of this file for pyra.rb This is where it might get dropped
    # byt the installer
    this_file_fullpath = op.abspath(op.dirname(__file__))
    candidates.append(op.join(this_file_fullpath, "pyra.rb"))
    candidates.append(op.join(this_file_fullpath, "Pyramid-Scheme", "pyra.rb"))

    # Finally check the home directory
    home_dir = op.expanduser("~")
    if home_dir != "~":
        # home_dir got expanded aka it is known
        candidates.append(op.join(home_dir, "pyra.rb"))
        candidates.append(op.join(home_dir, "Pyramid-Scheme", "pyra.rb"))

    if verbose > 1:
        print(f"Looking for pyra.rb in {len(candidates)} locations:")

    pyra_rb = None
    for candidate in candidates:
        if op.isfile(candidate):
            with open(candidate) as f:
                file_hash = hashlib.md5(f.read().encode("utf-8")).hexdigest()
            if file_hash == EXPECTED_HASH:
                # This is the correct version of pyra.rb
                pyra_rb = candidate
                if verbose > 1:
                    print(f" {candidate} is the correct version of pyra.rb")
                break
            else:
                if verbose > 1:
                    print(f" {candidate} has the wrong hash ({file_hash} != {EXPECTED_HASH})")
        else:
            if verbose > 1:
                print(f" {candidate} does not exist")

    return pyra_rb


@register_subcommand(Subcommand.RUN)
def _(args: argparse.Namespace, extra: list[str]) -> None:
    """Main function for the command-line operation"""

    # rind ruby
    ruby = shutil.which("ruby")
    if ruby is None:
        raise RuntimeError("Could not find ruby executable. Make sure ruby is installed.")

    if args.verbose > 1:
        print("Ruby executable:", ruby)

    # get ruby version
    ruby_version = subprocess.check_output([ruby, "--version"]).decode("utf-8").strip()
    if args.verbose > 1:
        print("Ruby version:", ruby_version)

    pyra_rb = find_pyra_rb(args.verbose)

    if pyra_rb is None:
        raise RuntimeError("Could not find pyra.rb. Make sure pyramid scheme is installed.")

    if args.verbose > 1:
        print("pyra.rb:", pyra_rb)

    # run pyramid scheme
    if args.verbose:
        print("Running pyramid scheme:")

    subprocess.run([ruby, pyra_rb, args.input, *extra])


@register_subcommand(Subcommand.COMPILE_AND_RUN)
def _(args: argparse.Namespace, extra: list[str]) -> None:
    """Main function for the command-line operation"""

    # Get a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_output = op.join(tmpdir, "out.pyra")

        if args.verbose > 1:
            print("Temporary output file:", temp_output)

        args.output = temp_output

        # We don't care about these options for the compile step
        # This is just a convenience function to run the psll code
        args.full_names = False
        args.considerate_optimisation = False
        args.greedy_optimisation = False
        Subcommand.COMPILE.run(args, extra)

        # Run
        args.input = args.output
        Subcommand.RUN.run(args, extra)


@register_subcommand(Subcommand.DOWNLOAD_PYRA)
def _(args: argparse.Namespace, extra: list[str]) -> None:
    pyra_rb = find_pyra_rb(args.verbose)

    if pyra_rb is not None and not args.force:
        ans = input(f"Pyramid scheme found at {pyra_rb}. Re-download? [y/N] ")
        if ans.lower() != "y":
            return

    if args.verbose:
        print("Downloading pyramid scheme...")

    write_dir = None

    # Process priority options
    if args.here:
        write_dir = op.abspath(os.getcwd())
        if not os.access(write_dir, os.W_OK):
            raise RuntimeError(f"No write access to the current working directory ({write_dir})")

    elif args.home:
        home_dir = op.expanduser("~")
        if home_dir != "~":
            # home_dir got expanded aka it is known
            if os.access(home_dir, os.W_OK):
                write_dir = home_dir
            else:
                if args.verbose > 1:
                    print(f"No write access to home directory ({home_dir})")
        else:
            if args.verbose > 1:
                print("Cannot determine home directory")

    elif args.directory:
        if os.access(args.directory, os.W_OK):
            write_dir = args.directory
        else:
            if args.verbose > 1:
                print(f"No write access to specified directory ({args.directory})")

    if write_dir is None:
        # If there are no priority options

        this_file_dir = op.dirname(op.abspath(__file__))
        if os.access(this_file_dir, os.W_OK):
            write_dir = this_file_dir

    if write_dir is None:
        home_dir = op.expanduser("~")
        if home_dir != "~":
            # home_dir got expanded aka it is known
            if os.access(home_dir, os.W_OK):
                write_dir = home_dir
            else:
                if args.verbose > 1:
                    print(f"No write access to home directory ({home_dir})")

    if write_dir is None:
        raise RuntimeError("Could not find a suitable directory to write to")
    else:
        if args.verbose > 1:
            print("Found a suitable directory to write to:", write_dir)

    import urllib.request

    with tempfile.TemporaryDirectory() as tmpdir:
        with urllib.request.urlopen(PYRA_RB_URL) as response:
            pyra_rb = response.read().decode("utf-8")

        if pyra_rb is None:
            raise RuntimeError("Could not download pyra.rb")

        downloaded_hash = hashlib.md5(pyra_rb.encode("utf-8")).hexdigest()

        if downloaded_hash != EXPECTED_HASH:
            raise RuntimeError(f"Downloaded pyra.rb has the wrong hash ({downloaded_hash} != {EXPECTED_HASH}).")

        with open(op.join(tmpdir, "pyra.rb"), "w") as f:
            f.write(pyra_rb)

        if args.verbose > 1:
            print("Downloaded pyra.rb to", op.join(tmpdir, "pyra.rb"))

        shutil.copy(op.join(tmpdir, "pyra.rb"), op.join(write_dir, "pyra.rb"))


check_all_subcommands_registered()


# Called as a script
def argparse_and_main() -> None:  # pragma: no cover
    args, extra = parse_args()
    args.subcommand.run(args, extra)


# Called as a module
if __name__ == "__main__":  # pragma: no cover
    argparse_and_main()
