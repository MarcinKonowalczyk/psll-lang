import os

from setuptools import setup

__time_file_dir__ = os.path.dirname(os.path.realpath(__file__))
__version_file__ = os.path.join(__time_file_dir__, "psll", "__init__.py")
__version__ = None

with open(__version_file__) as f:
    for line in f.readlines():
        if line.startswith("__version__"):
            __version__ = line.split("=")[1].strip().strip('"')
            break

if __version__ is None:
    raise RuntimeError(f"Could not find __version__ in {__version_file__}")
else:
    print(f"Found __version__ = {__version__}")

setup(version=__version__)
