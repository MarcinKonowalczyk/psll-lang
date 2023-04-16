import argparse
import os.path as op


def valid_input_file(filename: str) -> str:
    if not op.exists(filename):
        raise argparse.ArgumentTypeError(f"The file {filename} does not exist!")
    if op.splitext(filename)[1] != ".psll":
        raise argparse.ArgumentTypeError(
            "The input file does not have an .psll extension!"
        )
    return filename


def arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile lisp-like syntax to Pyramid Scheme",
    )

    subparsers = parser.add_subparsers(required=True, dest="subcommand")

    compile_parser = subparsers.add_parser(
        "compile",
        help="compile a psll program to a pyramid scheme program",
    )

    compile_parser.add_argument(
        "input",
        type=valid_input_file,
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

    # Compiler options
    # compile_parser.add_argument('-nt','--null-trees', action='store_true',
    #     help='Use null (height 0) trees.')
    # compile_parser.add_argument('--dot-spaces', action='store_true',
    #     help='Render spaces as dots')

    subparsers.add_parser(
        "run",
        help="run a pyramid scheme program",
    )

    subparsers.add_parser(
        "compile-and-run",
        help="compile and run a psll program",
    )

    args = parser.parse_args()

    if args.subcommand == "compile":
        if args.output == "":
            pass
        elif args.output == " ":
            args.output = op.splitext(args.input)[0] + ".pyra"
        if op.exists(args.output) and not args.force:
            answer = input(f"File {args.output} already exists. Overwrite? [y/N]")
            if answer.lower() != "y":
                args.output = None
        if op.splitext(args.output)[1] != ".pyra":
            raise argparse.ArgumentTypeError(
                "The output file does not have an .pyra extension!"
            )
    elif args.subcommand == "run":
        print(
            "Running pyramid scheme programs from this script is not yet implemented."
        )
        exit(1)
    elif args.subcommand == "compile-and-run":
        print(
            "Running pyramid scheme programs from this script is not yet implemented."
        )
        exit(1)
    else:
        raise RuntimeError("This should never happen!")

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


# Called as a script
def argparse_and_main() -> None:  # pragma: no cover
    args = arg_parser()
    if args.subcommand == "compile":
        subcommand_compile(args)


# Called as a module
if __name__ == "__main__":  # pragma: no cover
    argparse_and_main()
