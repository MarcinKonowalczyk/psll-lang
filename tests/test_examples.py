import unittest

import os
from os.path import exists, splitext

# TODO change to subprocess.run
import subprocess
from functools import partial

shell = partial(subprocess.run, shell=True, stdout=subprocess.PIPE)

pyra_path = os.getcwd() + "/Pyramid-Scheme/pyra.rb"
pyra_exists = exists(pyra_path)
print("pyra.rb path:", pyra_path)
print("exists:", pyra_exists)

# spell-checker: disable-next-line
ruby_path = os.popen("which ruby").read().replace("\n", "")
ruby_exists = exists(ruby_path)
print("ruby path:", ruby_path)
print("exists:", ruby_exists)

examples = "./examples/"


def skipUnlessExampleExists(filename):
    """Skip the test unless the example file exists"""

    def obj_wrapper(obj):
        if exists(filename):
            obj.filename = filename
            return obj
        else:
            reason = f"No '{filename}' found"
            return unittest.skip(reason)(obj)

    return obj_wrapper


# TODO This is somewhat messy with all those paths...
class MetaTests:
    def test_compiles(self):
        path, ext = splitext(self.filename)
        pyra_filename = path + ".pyra"
        if exists(pyra_filename):
            os.remove(pyra_filename)

        commands = [f"psll compile {self.filename} -o -f"]
        # commands = [commands[0], commands[0] + ' -go'] # Also test with greedy optimisation
        for com in commands:
            with self.subTest(command=com):
                s = shell(com)
                if s.returncode != 0:
                    self.fail("Compilation unsuccessful!")
                else:
                    # out = s.stdout.decode("utf-8")
                    # out = (' > ' + l for l in out.split('\n') if l)
                    # print('\nPsll compiler output:')
                    # print('\n'.join(out))
                    pass
                self.assertTrue(exists(pyra_filename), ".pyra file not generated")

    @unittest.skipUnless(ruby_exists, "No ruby found")
    @unittest.skipUnless(pyra_exists, "No pyra.rb found")
    def test_runs(self):
        path, ext = splitext(self.filename)
        pyra_filename = path + ".pyra"

        # TODO What if the script takes a command line input? (Add timeout?)
        # TODO Capture stdout better

        commands = [f"psll compile {self.filename} -o -f"]
        # commands = [commands[0], commands[0] + ' -go'] # Also test with greedy optimisation
        for psll_com in commands:
            rb_com = f"{ruby_path} {pyra_path} {pyra_filename}"
            with self.subTest(command=psll_com):
                shell(psll_com)  # Recompile
                s = shell(rb_com)
                if s.returncode != 0:
                    self.fail("Pyramid Scheme code does not run!")
                else:
                    # out = s.stdout.decode("utf-8")
                    # out = (' > ' + l for l in out.split('\n') if l)
                    # print('\nPyramid Scheme output:')
                    # print('\n'.join(out))
                    pass


# spell-checker: words nargin
@skipUnlessExampleExists(examples + "nargin_counter.psll")
class TestNarginCounter(unittest.TestCase, MetaTests):
    pass


@skipUnlessExampleExists(examples + "xor.psll")
class TestXOR(unittest.TestCase, MetaTests):
    pass


@skipUnlessExampleExists(examples + "bubble_sort.psll")
class TestBubbleSort(unittest.TestCase, MetaTests):
    pass


@skipUnlessExampleExists(examples + "def_keyword.psll")
class TestDefKeyword(unittest.TestCase, MetaTests):
    pass


@skipUnlessExampleExists(examples + "arrays.psll")
class TestArray(unittest.TestCase, MetaTests):
    pass


@skipUnlessExampleExists(examples + "binary_operator_chains.psll")
class TestOperatorChains(unittest.TestCase, MetaTests):
    pass


# spell-checker: words PRNG
@skipUnlessExampleExists(examples + "linear_congruential_generator.psll")
class TestPRNG(unittest.TestCase, MetaTests):
    pass


if __name__ == "__main__":
    unittest.main()
