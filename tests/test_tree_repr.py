import unittest

from string import ascii_letters
from random import choice
from itertools import product

# Add '.' to path so running this file by itself also works
import os, sys
sys.path.append(os.path.realpath('.'))

from tree_repr import Pyramid

class Pyramids(unittest.TestCase):

    def test_creation(self):
        ''' Create a few pyramids '''
        contents = ['','!','hi','sup','hola','salut','hellos','regards','morning!',"Howdy'll",'greetings','blue skies']
        for c in contents:
            tree_repr = Pyramid.from_text(c)

if __name__ == '__main__':
    unittest.main()