import unittest

from string import ascii_letters
from random import choice
from itertools import product, permutations

# Add '.' to path so running this file by itself also works
import os, sys
sys.path.append(os.path.realpath('.'))

import tree_repr
from tree_repr import Pyramid

from contextlib import contextmanager
from io import StringIO

@contextmanager
def capture_output():
    old = sys.stdout
    try:
        sys.stdout = StringIO()
        yield sys.stdout
    finally:
        sys.stdout = old

random_string = lambda N: ''.join(choice(ascii_letters) for _ in range(N)) 

TEST_CONTENT = ['','!','hi','sup','hola','salut','hellos','regards','morning!',"Howdy'll",'greetings']
TEST_PYRAMIDS = [' ^ \n - ',
'  ^  \n /!\\ \n --- ',
'   ^   \n  / \\  \n /hi \\ \n ----- ',
'   ^   \n  / \\  \n /sup\\ \n ----- ',
'   ^   \n  /h\\  \n /ola\\ \n ----- ',
'    ^    \n   / \\   \n  /   \\  \n /salut\\ \n ------- ',
'    ^    \n   / \\   \n  /hel\\  \n / los \\ \n ------- ',
'    ^    \n   /r\\   \n  /ega\\  \n / rds \\ \n ------- ',
'    ^    \n   /m\\   \n  /orn\\  \n /ing! \\ \n ------- ',
'    ^    \n   /H\\   \n  /owd\\  \n /y\'ll \\ \n ------- ',
'    ^    \n   /g\\   \n  /ree\\  \n /tings\\ \n ------- ']

class Pyramids(unittest.TestCase):

    def test_creation(self):
        ''' Create few pyramids '''
        for c in TEST_CONTENT:
            with self.subTest(content=c):
                p = Pyramid.from_text(c)

    def test_default_space(self):
        ''' Make sure the default space is a space '''
        self.assertEqual(tree_repr.SPACE,' ')
    
    def test_output(self):
        ''' Check output is what it is supposed to be '''
        for c,p in zip(TEST_CONTENT,TEST_PYRAMIDS):
            with self.subTest(content=c):
                with capture_output() as output:
                    print(Pyramid.from_text(c),end='')
                self.assertEqual(output.getvalue(),p)
        
    def test_min_width(self):
        ''' Create a few pyramids, but now with minimum width '''
        for c,w in product(TEST_CONTENT,range(10)):
            with self.subTest(content=c,min_width=w):
                p = Pyramid.from_text(c,min_width=w)

    def test_remove_spaces(self):
        ''' '''
        p = Pyramid.from_text('  ! ',remove_spaces=False)
        target = '   ^   \n  / \\  \n / ! \\ \n ----- '
        with capture_output() as output:
            print(p,end='')
        self.assertEqual(output.getvalue(),target)

if __name__ == '__main__':
    unittest.main()