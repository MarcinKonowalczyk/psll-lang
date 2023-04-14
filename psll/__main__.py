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


def valid_output_file(args: argparse.Namespace, ext: str = ".pyra") -> None:
    filename = args.output
    if not filename:
        return  # Return if no -o option
    # Make filename based on the input filename
    if filename == " ":
        filename = op.splitext(args.input)[0] + ext
        args.output = filename
    # Check whether to overwrite
    if op.exists(filename) and not args.force:
        answer = input(f"File {filename} already exists. Overwrite? [y/N]")
        if answer.lower() != "y":
            args.output = None
    # Check extension
    if op.splitext(filename)[1] != ext:
        raise argparse.ArgumentTypeError(
            "The output file does not have an .pyra extension!"
        )


parser = argparse.ArgumentParser(
    description="Compile lisp-like syntax to Pyramid Scheme"
)
parser.add_argument(
    "input",
    type=valid_input_file,
    help=(
        "Input file written in the pyramid scheme (lisp (like)) syntax, with the"
        " .psll expension."
    ),
)
parser.add_argument(
    "-o",
    dest="output",
    required=False,
    metavar="output",
    nargs="?",
    default=None,
    const=" ",
    help=(
        'Output pyramid scheme. If "output" is supplied, the pyramid scheme is'
        ' saved to that filename. If no "output" is supplied (aka just the -o'
        " option) the pyramid scheme is saved to the filename matching the input"
        " filename, with the .pyra extension."
    ),
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Run in the verbose mode."
)
parser.add_argument("-f", "--force", action="store_true", help="Force file overwrite.")

parser.add_argument(
    "--full-names",
    action="store_true",
    help=(
        "Don't shorten variable names when compiling the pyramid scheme. This will"
        " result in longer, but potentially more readable source code. Usefull for"
        " either compiler or pyramid scheme debugging."
    ),
)

parser.add_argument(
    "-go",
    "--greedy-optimisation",
    action="store_true",
    help=(
        "Greedily insert an empty pyramid the very first place which minimised the"
        " size is beneficial. This tends to result in tall source code."
    ),
)
parser.add_argument(
    "-co",
    "--considerate-optimisation",
    action="store_true",
    help=(
        "Consider all the possible places to insert a pyramid, up to certain depth."
        " Choose the most beneficial. This tends to result in wide source code."
    ),
)

# Compiler options
# parser.add_argument('-nt','--null-trees', action='store_true',
#     help='Use null (height 0) trees.')
# parser.add_argument('--dot-spaces', action='store_true',
#     help='Render spaces as dots')

args = parser.parse_args()
valid_output_file(args)

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


def main(args: argparse.Namespace) -> None:  # pragma: no cover
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


main(args)
