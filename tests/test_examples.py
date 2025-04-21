import glob
import hashlib
import os
import subprocess
from functools import partial
from typing import Callable, Optional

import pytest
from conftest import Subtests

# Get all the example outputs from the examples_outputs directory

__this_file_dir__ = os.path.dirname(os.path.abspath(__file__))
__examples_dir__ = os.path.abspath(os.path.join(__this_file_dir__, "..", "examples"))
__output_dir__ = os.path.join(__this_file_dir__, "examples_outputs")

if not os.path.isdir(__output_dir__):
    raise RuntimeError(f"Could not find examples_outputs directory: {__output_dir__}")

# Find all the examples
EXAMPLES_OUTPUT: dict[str, str] = {}

for example in glob.glob(os.path.join(__output_dir__, "*.txt")):
    basename = os.path.basename(example)
    basename = os.path.splitext(basename)[0]
    basename, expected_hash = basename.rsplit("-", 1)

    with open(example) as f:
        expected_output = f.read()

    expected_filename = os.path.join(__examples_dir__, basename + ".psll")

    if not os.path.exists(expected_filename):
        raise RuntimeError(f"Could not find expected file {expected_filename}")

    with open(expected_filename) as f:
        actual_hash = hashlib.md5(f.read().encode("utf-8")).hexdigest()

    if actual_hash != expected_hash:
        raise RuntimeError(f"Hash mismatch for {expected_filename}: {actual_hash} != {expected_hash}")

    # psll_examples.append((expected_filename, expected_output))
    EXAMPLES_OUTPUT[basename] = expected_output


def compare_with_expected(
    basename: str,
    actual: str,
    recover_stack: Optional[list[Callable[[str, str], None]]] = None,
) -> None:
    """Compare the actual output with the expected output. If a line does not match, attempt to recover using the
    recover stack. The first function in the recover stack that does not raise an AssertionError will
    count as a recovery."""
    recover_stack = recover_stack or []

    expected = EXAMPLES_OUTPUT.get(basename)
    assert expected is not None, f"Could not find expected output for {basename}"
    actual_lines, expected_lines = actual.splitlines(), expected.splitlines()
    assert len(actual_lines) == len(expected_lines), "Output length mismatch"
    for i, (a, e) in enumerate(zip(actual_lines, expected_lines)):
        if a == e:
            continue
        for recover in recover_stack:
            try:
                recover(a, e)
                break
            except AssertionError:
                pass
        else:
            pytest.fail(f"Output mismatch at line {i + 1}:\nExpected: {e}\nActual: {a}")


def recover_float(a: str, e: str, tol: float = 1e-10) -> None:
    """Recover from a float mismatch"""
    try:
        a_float = float(a)
        e_float = float(e)
        assert abs(a_float - e_float) < tol, f"Output mismatch: {a} != {e}"
    except ValueError:
        raise AssertionError(f"Cannot parse as float: {a} != {e}") from None


def recover_array_example_line(a: str, e: str, tol: float = 1e-10) -> None:
    E_LINE = 'a: [1, "hello", "farewell", 3.3]'
    if e != E_LINE:
        raise AssertionError(f"Expected line {E_LINE} but got {e}")

    # ok, we're at the line which causes an error. try to parse the float out of it
    try:
        a_float = float(a.split(",")[-1].strip("]"))
        e_float = float(e.split(",")[-1].strip("]"))
        assert abs(a_float - e_float) < tol, f"Output mismatch: {a} != {e}"
    except ValueError:
        raise AssertionError(f"Cannot parse as float: {a} != {e}") from None


TEST_CASES: list[tuple[str, Callable[[str, str], None]]] = [
    ("arrays", partial(compare_with_expected, recover_stack=[recover_array_example_line])),
    ("binary_operator_chains", partial(compare_with_expected, recover_stack=[recover_float])),
    ("bubble_sort", compare_with_expected),
    ("comparisons", compare_with_expected),
    ("def_keyword", compare_with_expected),
    ("linear_congruential_generator", partial(compare_with_expected, recover_stack=[recover_float])),
    ("modulo_function", compare_with_expected),
    ("nargin_counter", compare_with_expected),
    ("xor", compare_with_expected),
]


def compile_and_run(
    filename: str,
    ruby: Optional[str] = None,
    pyra: Optional[str] = None,
) -> str:
    """Compile and run the given file, returning the output"""
    args = ["psll", "compile-and-run"]
    if ruby:
        args += ["--ruby", ruby]
    if pyra:
        args += ["--pyra", pyra]
    args += [filename]
    return subprocess.check_output(
        args,
        stderr=subprocess.STDOUT,
        text=True,
    )


def compile(input_filename: str, output_filename: str, args: Optional[list[str]] = None) -> None:
    """Compile the given input file to the given output file"""
    args = args or []
    subprocess.check_call(
        ["psll", "compile", input_filename, "-o", output_filename, "--force"] + args,
        stderr=subprocess.STDOUT,
        text=True,
    )


def run(filename: str) -> str:
    """Run the given file, returning the output"""
    return subprocess.check_output(
        ["psll", "run", filename],
        stderr=subprocess.STDOUT,
        text=True,
    )


def test_examples(
    ruby: Optional[str],
    pyra: Optional[str],
    subtests: Subtests,
) -> None:
    """Test that the examples compile and run correctly"""
    for basename, compare in TEST_CASES:
        with subtests.test(basename=basename):
            filename = os.path.join(__examples_dir__, basename + ".psll")
            output = compile_and_run(filename, ruby=ruby, pyra=pyra)
            compare(basename, output)


# @pytest.mark.parametrize("filename, expected_output", psll_examples)
# def test_with_greedy_optimisation(filename: str, expected_output: str) -> None:
#     """Test just the compile command, with a bunch of optimisation flags"""

#     with tempfile.TemporaryDirectory() as tmpdir:
#         temp_filename = os.path.join(tmpdir, os.path.basename(filename) + ".pyra")
#         compile(filename, temp_filename, args=[])
#         assert run(temp_filename) == expected_output, f"Example {filename} output mismatch"

#         compile(filename, temp_filename, args=["-go"])
#         assert run(temp_filename) == expected_output, f"Example {filename} output mismatch"

#         # compile(filename, temp_filename, args=['-co'])
#         # assert run(temp_filename) == expected_output, f"Example {filename} output mismatch"


# # TODO: Test optimisations
