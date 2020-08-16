import unittest

from string import ascii_letters
import random
from itertools import product, permutations

# Add '.' to path so running this file by itself also works
import os, sys
sys.path.append(os.path.realpath('.'))

import psll

from contextlib import contextmanager

random_string = lambda N: ''.join(random.choice(ascii_letters) for _ in range(N)) 

def random_tree(max_depth=10,str_prob=0.6):
    ''' Make up a random tree '''
    ast = [random_string(random.randrange(4))]
    for _ in range(2):
        if random.random()<str_prob or max_depth==1:
            node = random_string(random.randrange(4))
        else:
            node = random_tree(max_depth=max_depth-1)
        ast.append(node)
    return ast

def depth(tree):
    ''' Calculate the depth of a tree '''
    if isinstance(tree,str):
        return 0
    elif isinstance(tree,list):
        return max(depth(node) for node in tree) + 1
    else:
        raise TypeError

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

class MetaTests:

    def paired_test(self,inputs,targets,fun):
        ''' Test input/target pairs with fun(input)==target '''
        self.assertEqual(len(inputs),len(targets))
        for i,t in zip(inputs,targets):
            with self.subTest(input=i):
                self.assertEqual(fun(i),t)

    def syntax_error_test(self,inputs,fun,error):
        ''' Test that text throws an error '''
        for i in inputs:
            with self.subTest(input=i):
                with self.assertRaises(error):
                    fun(i)

#==========================================================================================================
#                                                                                                          
#  #####  ##  ##      #####        ##  ##     ##  #####   ##   ##  ######                                
#  ##     ##  ##      ##           ##  ####   ##  ##  ##  ##   ##    ##                                  
#  #####  ##  ##      #####        ##  ##  ## ##  #####   ##   ##    ##                                  
#  ##     ##  ##      ##           ##  ##    ###  ##      ##   ##    ##                                  
#  ##     ##  ######  #####        ##  ##     ##  ##       #####     ##                                  
#                                                                                                          
#==========================================================================================================

class Readfile(unittest.TestCase,MetaTests):

    @staticmethod
    def readfile(content):
        ''' psll.readfile proxy '''
        with psll_file(content) as f:
            return psll.readfile(f)

    def test_empty(self):
        ''' > Read and parse files with empty brackets '''
        contents = ['','()','( )','()()','()()()','(())','() (())']
        targets = ['','()','()','() ()','() () ()','(())','() (())']
        self.paired_test(contents,targets,self.readfile)

    def test_simple(self):
        ''' > Read and parse files with simple contents '''
        contents = ['(set)','(hi)','(set 1)','(set hi 1)','(1 2 3 4)','(hi) (salut)']
        self.paired_test(contents,contents,self.readfile)

    def test_comments(self):
        ''' > Removing comments '''
        contents = ['// hi','() // hi','(\n// hi\n)','//(\n()','()\n//)','// hi\n()\n// hi','//()']
        targets = ['','()','()','()','()','()','']
        self.paired_test(contents,targets,self.readfile)
    
    def test_single_spaces(self):
        ''' > Only single spaces '''
        contents = ['( )','(  )','(   )','(     )']
        targets = ['()','()','()','()']
        self.paired_test(contents,targets,self.readfile)
    
    def test_leading_and_trailing_spaces(self):
        ''' > No leading or trailing whitepace '''
        contents = ['(   hi)','(hi   )','(hi   1)','(   hi 1)','(hi 1   )']
        targets = ['(hi)','(hi)','(hi 1)','(hi 1)','(hi 1)']
        self.paired_test(contents,targets,self.readfile)

    def test_multiline(self):
        ''' > Input over multiple lines '''
        contents = ['()\n()','\n(hi)','(\nhi)','(hi\n)','(hi)\n'];
        targets = ['() ()','(hi)','(hi)','(hi)','(hi)']
        self.paired_test(contents,targets,self.readfile)

#=============================================================
#                                                             
#  ##      #####  ##    ##                                    
#  ##      ##      ##  ##                                     
#  ##      #####    ####                                      
#  ##      ##      ##  ##                                     
#  ######  #####  ##    ##                                    
#                                                             
#=============================================================

class Split(unittest.TestCase,MetaTests):

    def test_simple(self):
        ''' > Simple inputs '''
        texts = ['','()','() ()','(hi)','(out 1)','(set a 1)']
        targets = [[],['()'],['()','()'],['(hi)'],['(out 1)'],['(set a 1)']]
        self.paired_test(texts,targets,psll.split_into_trees)

    def test_nested(self):
        ''' > Nested inputs '''
        texts = ['(())','(()) ()','(((hi)))','(() () hi)','(() ()) (()) ()']
        targets = [['(())'],['(())','()'],['(((hi)))'],['(() () hi)'],['(() ())','(())','()']]
        self.paired_test(texts,targets,psll.split_into_trees)

    def test_string(self):
        ''' > Bracket parity error '''
        texts = ['(',')',')(','(hi))','((hi)','((','))','((()())','(()()))']
        self.syntax_error_test(texts,psll.split_into_trees,psll.PsllSyntaxError)

    def test_simple_subtrees(self):
        ''' > Simple subtrees'''
        texts = ['(hi)','(set a 1)','(one two three four)']
        targets = [['hi'],['set','a','1'],['one','two','three','four']]
        self.paired_test(texts,targets,psll.split_into_subtrees)

    def test_nested_subtrees(self):
        ''' > Nested subtrees'''
        texts = ['(set a (= b 1))','(a (b (() c)))']
        targets = [['set','a',['=','b','1']],['a',['b',[[''],'c']]]]
        self.paired_test(texts,targets,psll.split_into_subtrees)

    def test_blank(self):
        ''' > Trees with blank elements '''
        texts = ['()','(())','(() hi)','(1 2)','((hi 1) (hi 2))']
        targets = [[''],[['']],[[''], 'hi'],['1','2'],[['hi','1'],['hi','2']]]
        self.paired_test(texts,targets,psll.split_into_subtrees)

    def test_quotes(self):
        ''' > Don't split quotes '''
        texts = ['("hi")','(\'hello\')','(set a \'one\')','(set b "two")']
        targets = [['"hi"'],['\'hello\''],['set','a','\'one\''],['set','b','"two"']]
        self.paired_test(texts,targets,psll.split_into_subtrees)

#=====================================================================================================
#                                                                                                     
#  #####   #####    #####            #####   #####     #####    ####                                
#  ##  ##  ##  ##   ##               ##  ##  ##  ##   ##   ##  ##                                   
#  #####   #####    #####  ########  #####   #####    ##   ##  ##                                   
#  ##      ##  ##   ##               ##      ##  ##   ##   ##  ##                                   
#  ##      ##   ##  #####            ##      ##   ##   #####    ####                                
#                                                                                                     
#=====================================================================================================

class TreeTraversal(unittest.TestCase,MetaTests):

    def test_string_fun(self):
        ''' Test that the string function is applied a correct number of times '''
        trees = [['a'],['a','b'],['a','b','c'],
        ['Quick',[['brown','fox'],['jumped',[['over']]],'a'],['lazy'],'dog']]
        counts = [1,2,3,8]

        def counter(node):
            global count
            count += 1
            return node

        def count_strings(tree):
            global count
            count = 0
            psll.tree_traversal(tree,str_fun=counter)
            return count
        
        self.paired_test(trees,counts,count_strings)

    def test_list_fun(self):
        ''' Test that the list function is applied a correct number of times '''
        trees = [['a'],['a','b'],['a','b','c'],
        ['Quick',[['brown','fox'],['jumped',[['over']]],'a'],['lazy'],'dog']]
        counts = [0,0,0,6]

        def counter(node):
            global count
            count += 1
            return node

        def count_lists(tree):
            global count
            count = 0
            psll.tree_traversal(tree,list_fun=counter)
            return count
        
        self.paired_test(trees,counts,count_lists)

    def test_tyep_error(self):
        ''' All elements of the tree must be strings or other trees '''
        trees = [[1,'int'],[set(),'set'],[{},'dict'],[(),'tuple'],
        ['Quick',[['brown','fox'],['jumped',[('over',)]],'a'],['lazy'],'dog']]
        self.syntax_error_test(trees,psll.tree_traversal,TypeError)

class StingExpansion(unittest.TestCase):

    def test_string_expansion(self):
        ''' > Make sure the prompt is expanded '''
        prompts = [random_string(N+1) for N in range(10)]
        for prompt in prompts:
            with self.subTest(prompt=prompt):
                ast = [f'"{prompt}"']
                est = psll.expand_all_stings([f'"{prompt}"'])
                self.assertGreater(depth(est),depth(ast))

    def test_double_quote(self):
        ''' > Make sure the " sign is *not* is expanded '''
        ast = ['"']
        est = psll.expand_all_stings(ast)
        self.assertEqual(ast,est)

    def test_quote_combinations(self):
        ''' > Expand some more strings as subtrees '''
        trees = [['.hi.'],['out','.hi.'],['.one.','.two.'],
            ['set','a','.hello.'],['set','.a.','hello'],
            ['.set.','a','hello']]
        for quote,ast in product('"\'',trees):
            ast = [t.replace('.',quote) for t in ast]
            with self.subTest(ast=ast):
                est = psll.expand_all_stings(ast)
                self.assertGreater(depth(est),depth(ast))
    
    def test_mixed_quotes(self):
        ''' > Mix correct quote pairs in one tree '''
        ast = ['"one"','\'two\'']
        est = psll.expand_all_stings(ast)
        self.assertGreater(depth(est),depth(ast))
    
    def test_nested(self):
        ''' > Expand strings in nested trees '''
        trees = [[['\'hi\'']],[['"hi"']],['set','a',['+','a','\'hi\'']],['set','a',['+','a','"hi"']]]
        for ast in trees:
            with self.subTest(ast=ast):
                est = psll.expand_all_stings(ast)
                self.assertGreater(depth(est),depth(ast))

#=======================================================================
#                                                                       
#  #####   ##   ##  ##  ##      ####                                  
#  ##  ##  ##   ##  ##  ##      ##  ##                                
#  #####   ##   ##  ##  ##      ##  ##                                
#  ##  ##  ##   ##  ##  ##      ##  ##                                
#  #####    #####   ##  ######  ####                                  
#                                                                       
#=======================================================================

# @unittest.skip("blah")
class BuildTree(unittest.TestCase,MetaTests):

    def test_simple(self):
        ''' > Simple trees '''
        trees = [[''],[' '],['hi'],['out','a'],['set','a','1']]
        targets = [' ^ \n - ',
            '  ^  \n / \\ \n --- ',
            '   ^   \n  / \\  \n /hi \\ \n ----- ',
            '     ^   \n    / \\  \n   /out\\ \n  ^----- \n /a\\     \n ---     ',
            '     ^     \n    / \\    \n   /set\\   \n  ^-----^  \n /a\\   /1\\ \n ---   --- ']
        fun = lambda tree: str(psll.build_tree(tree))
        self.paired_test(trees,targets,fun)

    def test_nested(self):
        ''' > Nested trees '''
        trees = [[' ',['sup']],['set','a',['+','1','1']],
            ['out',['chr','32'],'b'],
            ['loop',['!',['<=>','n','N']],['set','a',['+','a','1']]]]
        targets = ['     ^  \n    / \\ \n   ^--- \n  / \\   \n /sup\\  \n -----  ','     ^       \n    / \\      \n   /set\\     \n  ^-----^    \n /a\\   /+\\   \n ---  ^---^  \n     /1\\ /1\\ \n     --- --- ','         ^     \n        / \\    \n       /out\\   \n      ^-----^  \n     / \\   /b\\ \n    /chr\\  --- \n   ^-----      \n  / \\          \n /32 \\         \n -----         ','           ^           \n          / \\          \n         /   \\         \n        /loop \\        \n       ^-------^       \n      /!\\     / \\      \n     ^---    /set\\     \n    / \\     ^-----^    \n   /<=>\\   /a\\   /+\\   \n  ^-----^  ---  ^---^  \n /n\\   /N\\     /a\\ /1\\ \n ---   ---     --- --- ']
        fun = lambda tree: str(psll.build_tree(tree))
        self.paired_test(trees,targets,fun)

    def test_too_many(self):
        ''' > Invalid number of keywords in a bracket '''
        trees = [['one','two','three','four'],['1','2','3','4','5']]
        fun = psll.build_tree
        self.syntax_error_test(trees,fun,psll.PsllSyntaxError)

    def test_invalid(self):
        ''' > Invalid trees '''
        fun = psll.build_tree
        
        trees = [1,(),{},set,['set','a',1]]
        self.syntax_error_test(trees,fun,TypeError)
        # TODO Split this into multiple tests
        trees = [[],[['set'],'a','1']]
        self.syntax_error_test(trees,fun,AssertionError)

if __name__ == '__main__':
    unittest.main(verbosity=2,failfast=True)