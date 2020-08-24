import os
from os.path import exists, splitext

from platform import python_version_tuple 
version = tuple(int(x) for x in python_version_tuple())
assert version[0]==3

# TODO change to subprocess.run
import subprocess
from functools import partial
if version[1] <= 6:
    print('Python 3.6 -')
    shell = partial(subprocess.run,shell=True,stdout=subprocess.PIPE)
else:
    print('Python 3.7 +')
    shell = partial(subprocess.run,shell=True,capture_output=True)

pyra_path = os.getcwd() + '/Pyramid-Scheme/pyra.rb'
pyra_exists = exists(pyra_path)
print('pyra.rb path:', pyra_path)
print('exists:', pyra_exists)

ruby_path = os.popen('which ruby').read().replace('\n','')
ruby_exists = exists(ruby_path)
print('ruby path:', ruby_path)
print('exists:', ruby_exists)

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

        com = f'python psll.py {self.filename} -o -f'
        commands = (com, com + ' -go') #, com + ' -so')
        for com in commands:
            with self.subTest(command=com):
                s = shell(com)
                if s.returncode != 0:
                    self.fail('Compilation unsuccessful!')
                else:
                    # out = s.stdout.decode("utf-8")
                    # out = (' > ' + l for l in out.split('\n') if l)
                    # print('\nPsll compiler output:')
                    # print('\n'.join(out))
                    pass
                self.assertTrue(exists(pyra_filename),'.pyra file not generated')
    
    @unittest.skipUnless(ruby_exists,'No ruby found')
    @unittest.skipUnless(pyra_exists,'No pyra.rb found')
    def test_runs(self):
        path, ext = splitext(self.filename)
        pyra_filename = path + '.pyra'
        
        # TODO What if the script takes a command line input? (Add timeout?)
        # TODO Capture stdout better

        commands = f'python psll.py {self.filename} -o -f'
        commands = [commands,commands+' -go']
        for psll_com in commands:
            rb_com = f'{ruby_path} {pyra_path} {pyra_filename}'
            with self.subTest(command=psll_com):
                shell(psll_com) # Recompile
                s = shell(rb_com)
                if s.returncode != 0:
                    self.fail('Pyramid Scheme code does not run!')
                else:
                    # out = s.stdout.decode("utf-8")
                    # out = (' > ' + l for l in out.split('\n') if l)
                    # print('\nPyramid Scheme output:')
                    # print('\n'.join(out))
                    pass
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

@skipUnlessExampleExists(examples + 'def_keyword.psll')
class TestDefKeyword(unittest.TestCase,MetaTest):
    pass

if __name__=="__main__":
    unittest.main()
