import glob
import hashlib
import os
import subprocess
import tempfile
from typing import Optional

import pytest

# Get all the example outputs from the examples_outputs directory

__this_file_dir__ = os.path.dirname(os.path.abspath(__file__))
__examples_dir__ = os.path.abspath(os.path.join(__this_file_dir__, "..", "examples"))
__output_dir__ = os.path.join(__this_file_dir__, "examples_outputs")

if not os.path.isdir(__output_dir__):
    raise RuntimeError(f"Could not find examples_outputs directory: {__output_dir__}")

# Find all the examples
psll_examples: list[tuple[str, str]] = []
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

    psll_examples.append((expected_filename, expected_output))


def compile_and_run(filename: str) -> str:
    """Compile and run the given file, returning the output"""
    return subprocess.check_output(
        ["psll", "compile-and-run", filename],
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


@pytest.mark.parametrize("filename, expected_output", psll_examples)
def test_examples(filename: str, expected_output: str) -> None:
    """Test that the examples compile and run correctly"""
    assert compile_and_run(filename) == expected_output, f"Example {filename} output mismatch"


@pytest.mark.parametrize("filename, expected_output", psll_examples)
def test_examples_with_greedy_optimisation(filename: str, expected_output: str) -> None:
    """Test just the compile command, with a bunch of optimisation flags"""

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_filename = os.path.join(tmpdir, os.path.basename(filename) + ".pyra")
        compile(filename, temp_filename, args=[])
        assert run(temp_filename) == expected_output, f"Example {filename} output mismatch"

        compile(filename, temp_filename, args=["-go"])
        assert run(temp_filename) == expected_output, f"Example {filename} output mismatch"

        # compile(filename, temp_filename, args=['-co'])
        # assert run(temp_filename) == expected_output, f"Example {filename} output mismatch"


# TODO: Test optimisations
