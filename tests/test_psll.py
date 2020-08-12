import unittest

from string import ascii_letters
from random import choice
from itertools import product, permutations

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

class Split(unittest.TestCase):

    def paired_test(self,texts,targets,fun=psll.split_into_trees):
        ''' Test text/target pairs with fun(text)==target '''
        self.assertEqual(len(texts),len(targets))
        for text,target in zip(texts,targets):
            with self.subTest(text=text):
                self.assertEqual(fun(text),target)

    def syntax_error_test(self,texts):
        ''' Test that text throws a PsllSyntaxError '''
        for text in texts:
            with self.subTest(text=text):
                with self.assertRaises(psll.PsllSyntaxError):
                    psll.split_into_trees(text)

    def test_simple(self):
        ''' Simple inputs '''
        texts = ['','()','() ()','(hi)','(out 1)','(set a 1)']
        targets = [[],['()'],['()','()'],['(hi)'],['(out 1)'],['(set a 1)']]
        self.paired_test(texts,targets)

    def test_nested(self):
        ''' Nested inputs '''
        texts = ['(())','(()) ()','(((hi)))','(() () hi)','(() ()) (()) ()']
        targets = [['(())'],['(())','()'],['(((hi)))'],['(() () hi)'],['(() ())','(())','()']]
        self.paired_test(texts,targets)

    def test_string(self):
        ''' Bracket parity error '''
        texts = ['(',')',')(','(hi))','((hi)','((','))','((()())','(()()))']
        self.syntax_error_test(texts)

    def test_simple_subtrees(self):
        ''' Simple subtrees'''
        texts = ['(hi)','(set a 1)','(one two three four)']
        targets = [['hi'],['set','a','1'],['one','two','three','four']]
        self.paired_test(texts,targets,fun=psll.split_into_subtrees)

    def test_nested_subtrees(self):
        ''' Nested subtrees'''
        texts = ['(set a (= b 1))','(a (b (() c)))']
        targets = [['set','a',['=','b','1']],['a',['b',[[''],'c']]]]
        self.paired_test(texts,targets,fun=psll.split_into_subtrees)

    def test_blank(self):
        ''' Trees with blank elements '''
        texts = ['()','(())','(() hi)','(1 2)','((hi 1) (hi 2))']
        targets = [[''],[['']],[[''], 'hi'],['1','2'],[['hi','1'],['hi','2']]]
        self.paired_test(texts,targets,fun=psll.split_into_subtrees)

    def test_quotes(self):
        ''' Don't split quotes '''
        texts = ['("hi")','(\'hello\')','(set a \'one\')','(set b "two")']
        targets = [['"hi"'],['\'hello\''],['set','a','\'one\''],['set','b','"two"']]
        self.paired_test(texts,targets,fun=psll.split_into_subtrees)

# def BuildTree(unittest.TestCase):

#     def test_basic(self):

        
if __name__ == '__main__':
    unittest.main()