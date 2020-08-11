import unittest

from string import ascii_letters
from random import choice
from itertools import product

# Add '.' to path so running this file by itself also works
import os, sys
sys.path.append(os.path.realpath('.'))

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

class Pyramids(unittest.TestCase):

    def test_creation(self):
        ''' Create a and print few pyramids '''
        contents = ['','!','hi','sup','hola','salut','hellos','regards','morning!',"Howdy'll",'greetings','blue skies']
        for c in contents:
            with self.subTest(content=c):
                tree_repr = Pyramid.from_text(c)
                with capture_output() as output:
                    print(tree_repr)

if __name__ == '__main__':
    unittest.main()