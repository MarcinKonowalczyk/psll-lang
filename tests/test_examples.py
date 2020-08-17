import os
from os.path import exists, splitext

# TODO change to subprocess.run
import subprocess
from functools import partial
shell = partial(subprocess.call,shell=True)

pyra_path = os.getcwd() + '/Pyramid-Scheme/pyra.rb'
pyra_exists = exists(pyra_path)
print('pyra.rb path:', pyra_path, pyra_exists)

ruby_path = os.popen('which ruby').read().replace('\n','')
ruby_exists = exists(ruby_path)
print('ruby path:', ruby_path, ruby_exists)

import unittest

examples = './examples/'

def skipUnlessExampleExists(filename):
    ''' Skip the test unless the example file exists '''
    def obj_wrapper(obj):
        if exists(filename):
            obj.filename = filename
            return obj
        else:
            reason = f"No '{filename}' found"
            return unittest.skip(reason)(obj)
    return obj_wrapper

# TODO This is somewhat messy with all those paths...
class MetaTest:

    def test_compiles(self):
        path, ext = splitext(self.filename)
        pyra_filename = path + '.pyra'
        if exists(pyra_filename): os.remove(pyra_filename)

        command = f'python psll.py {self.filename} -o -f'
        if shell(command) != 0:
            self.fail('Compilation unsuccessful!')
        self.assertTrue(
            exists(pyra_filename),
            '.pyra file not generated')
    
    @unittest.skipUnless(ruby_exists,'No ruby found')
    @unittest.skipUnless(pyra_exists,'No pyra.rb found')
    def test_runs(self):
        path, ext = splitext(self.filename)
        pyra_filename = path + '.pyra'
        if exists(pyra_filename):
            shell(f'python psll.py {self.filename} -o -f')
        
        # TODO Capture stdout better
        command = f'{ruby_path} {pyra_path} {pyra_filename}'
        if shell(command) != 0:
            self.fail('Pyramid Scheme code does not run!')

@skipUnlessExampleExists(examples + 'nargin_counter.psll')
class TestNarginCounter(unittest.TestCase,MetaTest):
    pass

@skipUnlessExampleExists(examples + 'xor.psll')
class TestXOR(unittest.TestCase,MetaTest):
    pass

@skipUnlessExampleExists(examples + 'is_in_array.psll')
class TestIsInArray(unittest.TestCase,MetaTest):
    pass

@skipUnlessExampleExists(examples + 'bubble_sort.psll')
class TestBubbleSort(unittest.TestCase,MetaTest):
    pass


if __name__=="__main__":
    unittest.main()
