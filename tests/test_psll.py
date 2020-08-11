import unittest

from string import ascii_letters
from random import choice
from itertools import product

# Add '.' to path so running this file by itself also works
import os, sys
sys.path.append(os.path.realpath('.'))

import psll

from contextlib import contextmanager

random_string = lambda N: ''.join(choice(ascii_letters) for _ in range(N)) 

@contextmanager
def psll_file(content,filename=None):
    ''' Mock a .psll file with certain content '''
    if not filename: # Make temp filename
        filename = f'temp_{random_string(10)}.psll'
    try:
        with open(filename,'w') as f:
            f.write(content)
        yield filename
    finally:
        os.remove(filename)

class Readfile(unittest.TestCase):

    def paired_content_target(self,contents,targets):
        ''' Test Content/Target pairs '''
        self.assertEqual(len(contents),len(targets))
        for content,target in zip(contents,targets):
            with self.subTest(content=content,target=target):
                with psll_file(content) as f:
                    self.assertEqual(psll.readfile(f),target)

    def test_empty(self):
        ''' Read and parse files with empty brackets '''
        contents = ['','()','( )','()()','()()()','(())','() (())']
        targets = ['','()','()','() ()','() () ()','(())','() (())']
        self.paired_content_target(contents,targets)

    def test_simple(self):
        ''' Read and parse files with simple contents '''
        contents = ['(set)','(hi)','(set 1)','(set hi 1)','(1 2 3 4)','(hi) (salut)']
        self.paired_content_target(contents,contents)

    def test_comments(self):
        ''' Removing comments '''
        contents = ['// hi','() // hi','(\n// hi\n)','//(\n()','()\n//)','// hi\n()\n// hi','//()']
        targets = ['','()','()','()','()','()','']
        self.paired_content_target(contents,targets)
    
    def test_single_spaces(self):
        ''' Only single spaces '''
        contents = ['( )','(  )','(   )','(     )']
        targets = ['()','()','()','()']
        self.paired_content_target(contents,targets)
    
    def test_leading_and_trailing_spaces(self):
        ''' No leading or trailing whitepace '''
        contents = ['(   hi)','(hi   )','(hi   1)','(   hi 1)','(hi 1   )']
        targets = ['(hi)','(hi)','(hi 1)','(hi 1)','(hi 1)']
        self.paired_content_target(contents,targets)

    def test_multiline(self):
        ''' Input over multiple lines '''
        contents = ['()\n()','\n(hi)','(\nhi)','(hi\n)','(hi)\n'];
        targets = ['() ()','(hi)','(hi)','(hi)','(hi)']
        self.paired_content_target(contents,targets)


if __name__ == '__main__':
    unittest.main()