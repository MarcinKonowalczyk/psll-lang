"""
Run all the examples in the examples folder and record the output.
"""

# import sys
import glob
import hashlib
import os
import shutil
import subprocess

__this_file_dir__ = os.path.dirname(os.path.abspath(__file__))
__examples_dir__ = os.path.abspath(os.path.join(__this_file_dir__, "..", "examples"))
__outputs_dir__ = os.path.join(__this_file_dir__, "examples_outputs")

if not os.path.isdir(__examples_dir__):
    raise RuntimeError(f"Could not find examples directory: {__examples_dir__}")

if not os.path.isdir(__outputs_dir__):
    os.mkdir(__outputs_dir__)

# ==============================================================================

# Find all the examples
psll_examples = glob.glob(os.path.join(__examples_dir__, "*.psll"))

print(f"Found {len(psll_examples)} examples.")

# Exclude some examples since they take user input
exclude = [
    "golf_pyramid_scheme_negation",
    "favourite_number",
]

filenames: dict[str, str] = {}
for example in psll_examples:
    basename = os.path.basename(example)
    basename = os.path.splitext(basename)[0]
    if basename in exclude:
        continue
    filenames[basename] = example

already_recorded = glob.glob(os.path.join(__outputs_dir__, "*.txt"))

for name, filename in filenames.items():
    # Figure out the output filename
    with open(filename) as f:
        file_md5_hash = hashlib.md5(f.read().encode("utf-8")).hexdigest()
    output_filename = os.path.join(__outputs_dir__, f"{name}-{file_md5_hash}.txt")

    # Check if a file with the same same name (but maybe different hash) exists
    skip = False
    for recorded_filename in already_recorded:
        if os.path.basename(recorded_filename).startswith(f"{name}-"):
            old_hash = os.path.basename(recorded_filename).split("-", 1)[1].split(".")[0]
            if old_hash == file_md5_hash:
                print(f"Output for example {name} already recorded.")
                skip = True
            else:
                shutil.copyfile(recorded_filename, f"{recorded_filename}~")
                os.remove(recorded_filename)
                print(f"Output for example {name} has changed. Old output saved to *.txt~")
    if skip:
        continue

    # Run the example
    # TODO: should we invoke compile.py instead?
    try:
        output = subprocess.check_output(
            ["psll", "compile-and-run", filename],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError:
        print(f"Error running {filename}")
        continue

    print(f"Writing output to {output_filename}")
    if os.path.isfile(output_filename):
        shutil.copyfile(output_filename, f"{output_filename}~")
        os.remove(output_filename)

    with open(output_filename, "w") as f:
        f.write(output)
