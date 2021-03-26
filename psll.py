#!/usr/bin/python3

import re

from itertools import chain #, product, zip_longest
from more_itertools import windowed, windowed_complete

from functools import partial, reduce
from functools import lru_cache as cached
import operator
from string import ascii_letters

import sys
if sys.version_info<(3,6):
    raise RuntimeError('Upgrade to python 3.6, or newer.') # pragma: no cover

from ascii_trees import Pyramid

def in_pairs(iterable,in_tuple=False):
    ''' Pair up elements in the array. (s1,s2,s3,s4,s5) -> ((s1,s2),(s3,s4),s5) '''
    for p in windowed(iterable,2,step=2):
        yield p if p[1] else ((p[0],) if in_tuple else p[0])

is_string = lambda x: isinstance(x, str)
is_tuple = lambda x: isinstance(x, tuple)
# ^ Alas this cannot be done with partial

SPACE = ' '
PS_KEYWORDS = {'+','*','-','/','^','=','<=>','out','chr','arg','#','"','!','[',']','set','do','loop','?'}

class PsllSyntaxError(SyntaxError):
    pass

#==========================================================================================================
#                                                                                                          
#  #####  ##  ##      #####        ##  ##     ##  #####   ##   ##  ######                                
#  ##     ##  ##      ##           ##  ####   ##  ##  ##  ##   ##    ##                                  
#  #####  ##  ##      #####        ##  ##  ## ##  #####   ##   ##    ##                                  
#  ##     ##  ##      ##           ##  ##    ###  ##      ##   ##    ##                                  
#  ##     ##  ######  #####        ##  ##     ##  ##       #####     ##                                  
#                                                                                                          
#==========================================================================================================

def readfile(filename):
    ''' Read the file, remove comments and make sure all the lines are in correct brackets '''

    with open(filename,'r') as f:
        text = f.read()

    subs = ((r'//.*',''), # Remove comments
        (r'\n+',''), # Remove newlines
        (r'((?<=^)\s+|\s+(?=$))',''), # No trailing or leading whitespace
        (r'((?<=\()\s+|\s+(?=\)))',''), # Spaces inside brackets
        (r'(?<=\))(?=\()',' ')) # Put single spaces between crammed brackets

    # Apply substitutions
    for a,b in subs:
        text = re.sub(a,b,text)

    return text

#=======================================================================================================================================
#                                                                                                                                       
#   ####   #####   ##     ##  ######  #####  ##    ##  ######         ####  #####   ##      ##  ######                                
#  ##     ##   ##  ####   ##    ##    ##      ##  ##     ##          ##     ##  ##  ##      ##    ##                                  
#  ##     ##   ##  ##  ## ##    ##    #####    ####      ##           ###   #####   ##      ##    ##                                  
#  ##     ##   ##  ##    ###    ##    ##      ##  ##     ##             ##  ##      ##      ##    ##                                  
#   ####   #####   ##     ##    ##    #####  ##    ##    ##          ####   ##      ######  ##    ##                                  
#                                                                                                                                       
#=======================================================================================================================================

def context_split(string, delimiter=',', contexts=(), escape_char='\\', remove_empty=False):
    ''' Split string at delimiter, except for in the middle of the specified contexts '''

    state = [0 for _ in contexts] # States of each context
    last_break, escape, parts = 0, False, [] # Keep track of 

    for si,char in enumerate(string):
        if escape:
            escape = False
            continue

        for ci,c in enumerate(contexts):
            if not any(state[ci+1:]):
                if state[ci]:
                    # First try to match the closing context if state is already high
                    # This make matching the same delimiter for opening and closing work
                    if char is c[1]: state[ci] -= 1
                    elif char is c[0]: state[ci] += 1
                else:
                    if char is c[0]: state[ci] += 1
                    elif char is c[1]: state[ci] -= 1

        escape = char is escape_char # Escape the next char

        if not any(state) and (char is delimiter or not delimiter):
            parts.append(string[last_break:si])
            if delimiter: si += 1 # Skip delimiter
            last_break = si

        if any(s<0 for s in state):
            raise PsllSyntaxError('Invalid context structure. Ketbra context match.')

    parts.append(string[last_break:])

    if any(state):
        raise PsllSyntaxError('Invalid context structure. Incomplete context.')
    
    if remove_empty:
        parts = [p for p in parts if p]

    return tuple(parts)

#=============================================================
#                                                             
#  ##      #####  ##    ##                                    
#  ##      ##      ##  ##                                     
#  ##      #####    ####                                      
#  ##      ##      ##  ##                                     
#  ######  #####  ##    ##                                    
#                                                             
#=============================================================

lexer_split = partial(context_split,delimiter=' ',contexts=('()','[]','""'),remove_empty=True)
incontext = lambda text,context: len(text)>=2 and text[0]==context[0] and text[-1]==context[1]

def lex(text):
    ''' Compose a basic abstract syntax tree from the reduced source '''
    return tuple((lex(s[1:-1]) if incontext(s,'()') else s) for s in lexer_split(text))

#==================================================================================================================================================
#                                                                                                                                                  
#  ######  #####    #####  #####        ######  #####      ###    ##   ##  #####  #####     ####    ###    ##                                    
#    ##    ##  ##   ##     ##             ##    ##  ##    ## ##   ##   ##  ##     ##  ##   ##      ## ##   ##                                    
#    ##    #####    #####  #####          ##    #####    ##   ##  ##   ##  #####  #####     ###   ##   ##  ##                                    
#    ##    ##  ##   ##     ##             ##    ##  ##   #######   ## ##   ##     ##  ##      ##  #######  ##                                    
#    ##    ##   ##  #####  #####          ##    ##   ##  ##   ##    ###    #####  ##   ##  ####   ##   ##  ######                                
#                                                                                                                                                  
#==================================================================================================================================================

def tree_traversal(ast, str_fun=None, post_fun=None, pre_fun=None, final_fun=None):
    ''' (Depth-first) walk through the abstract syntax tree and application of appropriate functions '''
    ast2 = [] # Since, ast is immutable, build a new ast
    for node in ast:
        if node is None:
            ast2.append(node)
        elif is_string(node):
            ast2.append(str_fun(node) if str_fun else node)
        elif is_tuple(node):
            node = pre_fun(node) if pre_fun else node
            node = tree_traversal(node, pre_fun=pre_fun, str_fun=str_fun, post_fun=post_fun, final_fun=final_fun)
            node = post_fun(node) if post_fun else node
            ast2.append(node)
        else:
            raise TypeError(f'The abstract syntax tree can contain only strings or other, smaller, trees, not {type(node)}')
    ast2 = tuple(ast2)
    if final_fun:
        final_fun(ast2)
    return ast2 # Return ast back as a tuple

__processing_stack__ = [] # Pre processign functions in order they ought to be applied
def in_processing_stack(fun):
    ''' Append function to the processing stack '''
    __processing_stack__.append(fun)
    return fun

#==================================================================================================================================================
#                                                                                                                                                  
#   ####  ##   ##   #####   #####    ######  #####  ##     ##        ##     ##    ###    ###    ###  #####   ####                                
#  ##     ##   ##  ##   ##  ##  ##     ##    ##     ####   ##        ####   ##   ## ##   ## #  # ##  ##     ##                                   
#   ###   #######  ##   ##  #####      ##    #####  ##  ## ##        ##  ## ##  ##   ##  ##  ##  ##  #####   ###                                 
#     ##  ##   ##  ##   ##  ##  ##     ##    ##     ##    ###        ##    ###  #######  ##      ##  ##        ##                                
#  ####   ##   ##   #####   ##   ##    ##    #####  ##     ##        ##     ##  ##   ##  ##      ##  #####  ####                                 
#                                                                                                                                                  
#==================================================================================================================================================

def find_variable_names(ast):
    ''' Find all the variable names used in the code '''
    names = set()
    def variable_finder(node):
        if len(node)==3:
            if node[0] == 'set' and is_string(node[1]):
                names.add(node[1])
    tree_traversal(ast,post_fun=variable_finder)
    return names


@in_processing_stack
def shorten_variable_names(ast):
    ''' Shorten variable names to single letter, is possible '''
    names = find_variable_names(ast)
    future_names = set(n for n in names if len(n)==1)
    rules = {}
    for name in names:
        if len(name)==1: # Name is already short
            rules[name] = name
        else:
            all_names = names.union(future_names)
            for letter in name:
                if letter not in all_names:
                    rules[name]=letter
                    future_names.add(letter)
                    break # Go to the next name
            else: # No break, aka all single letters in the variable name already used
                for letter in ascii_letters:
                    if letter not in all_names:
                        rules[name]=letter
                        future_names.add(letter)
                        break # Go to the next name
                else: # No break, aka all single letter names already taken
                    # Give up and don't shorten the name
                    rules[name]=name
                    future_names.add(name)

    def string_replacer(node): # Shorten the names
        return rules[node] if node in rules.keys() else node

    return tree_traversal(ast,str_fun=string_replacer)

#=============================================================================================================================
#                                                                                                                             
#  ####    #####  #####        ##  ##  #####  ##    ##  ##      ##   #####   #####    ####                                  
#  ##  ##  ##     ##           ## ##   ##      ##  ##   ##      ##  ##   ##  ##  ##   ##  ##                                
#  ##  ##  #####  #####        ####    #####    ####    ##  ##  ##  ##   ##  #####    ##  ##                                
#  ##  ##  ##     ##           ## ##   ##        ##     ##  ##  ##  ##   ##  ##  ##   ##  ##                                
#  ####    #####  ##           ##  ##  #####     ##      ###  ###    #####   ##   ##  ####                                  
#                                                                                                                             
#=============================================================================================================================

def apply_replacement_rules(ast,rules):
    ''' Apply replacement rules to the abstract syntax tree '''
    def singleton_tuple_replacer(node): #  Replace (f) by def of f
        return rules[node[0]] if len(node)==1 and node[0] in rules.keys() else node
    def string_replacer(node): #  Replace f by def of f
        return rules[node] if node in rules.keys() else node

    return tree_traversal(ast,
        pre_fun=singleton_tuple_replacer,
        str_fun=string_replacer)

@in_processing_stack
def def_keyword(ast):
    ''' Search for ('def','something',(...)) keywords '''

    defs = []
    def replacer(node):
        if len(defs)>0:
            for value,definition in reversed(defs):
                if node == value:
                    return definition
        return node

    def find_defs(node):
        if len(node)>0 and node[0]=='def':
            if not len(node)==3:
                raise PsllSyntaxError(f"'def' statement must have 3 members, not {len(node)} (node = {node})")
            if not is_string(node[1]) or not is_tuple(node[2]):
                raise PsllSyntaxError(f"'def' statement can only assign brackets to values, not {type(node[2])} to {type(node[1])}")
            if node[1]=='def':
                raise PsllSyntaxError(f"('def' 'def' (...)) structure is not allowed")
            defs.append( (node[1], apply_replacement_rules(node[2],dict(defs))) )
            return () # Return empty tuple
        return node
    
    def pop_def_stack(ast):
        for node in ast:
            if node == ():
                defs.pop()

    return tree_traversal(ast,
        str_fun=replacer,
        pre_fun=find_defs,
        final_fun=pop_def_stack)

#=======================================================================================
#                                                                                       
#    ###    #####    #####      ###    ##    ##   ####                                
#   ## ##   ##  ##   ##  ##    ## ##    ##  ##   ##                                   
#  ##   ##  #####    #####    ##   ##    ####     ###                                 
#  #######  ##  ##   ##  ##   #######     ##        ##                                
#  ##   ##  ##   ##  ##   ##  ##   ##     ##     ####                                 
#                                                                                       
#=======================================================================================

@in_processing_stack
def range_keyword(ast):

    def ranger(node):
        if len(node)>0 and node[0]=='range':
            if not all(map(is_string,node[1:])):
                raise PsllSyntaxError(f"'range' arguments must be integer literals")
            if len(node)>4:
                raise PsllSyntaxError(f"'range' must be of the form (range begin end) or (range begin end step)")
            start, stop = int(node[1]), int(node[2])+1
            step = int(node[3]) if len(node)==4 else 1
            return ("[" + ', '.join(map(str,range(start,stop,step))) + "]",)
        return node

    return tree_traversal(ast,pre_fun=ranger)

# @in_processing_stack
# def len_keyword(ast):

#     def lengther(node):
#         if len(node)==3 and node[0]=='len':
#             if not all(map(is_string,node[1:])):
#                 raise PsllSyntaxError(f"'range' arguments must be variable names")
#             # return 
#             a, N = node[1], node[2]
#             ('set',N,0) ('loop', (), ())
#             # ( (set N 0) (loop (! (= (arg a N) nil)) (set N (+ N 1))) )

#     return tree_traversal(ast,pre_fun=lengther)


## TESTED
@in_processing_stack
def expand_array_literals(ast):

    def one_element_array(element):
        ''' Put `element` into a one-element array with the subtraction trick '''
        return ('-',(element,'0'),('0','0')) if element != '0' else ('-',(element,'1'),('1','1'))

    def array_to_tree(string):
        ''' Parse (inner) array string to its ast tree representation '''
        elements = lexer_split(string) # Reuse lexer split
        if not elements:
            return ('-',('0','0'),('0','0')) # Return empty array

        # Build the tree
        if len(elements) % 2:
            tree = one_element_array(elements[-1])
            elements = elements[:-1]
        else:
            tree = ()
        if elements:
            for e2,e1 in windowed(reversed(elements),2,step=2):
                tree = ('+', (e1,e2), tree) if tree else (e1,e2)

        return tree

    def array_expander(string):
        if incontext(string,'[]'):
            return array_to_tree(string[1:-1])
        return string

    return tree_traversal(ast,str_fun=array_expander)

#=========================================================================================
#                                                                                         
#   ####  ######  #####    ##  ##     ##   ####     ####                                
#  ##       ##    ##  ##   ##  ####   ##  ##       ##                                   
#   ###     ##    #####    ##  ##  ## ##  ##  ###   ###                                 
#     ##    ##    ##  ##   ##  ##    ###  ##   ##     ##                                
#  ####     ##    ##   ##  ##  ##     ##   ####    ####                                 
#                                                                                         
#=========================================================================================

## TESTED
@in_processing_stack
def expand_string_literals(ast):
    
    string_split = partial(context_split,delimiter='',contexts=('""',),remove_empty=True)

    def special(char):
        ''' Convert char to its special character representation '''
        cases = {'n':'\n', 't':'\t', 'r':'\r'}
        return cases[char] if char in cases else char

    def expand(string):
        if incontext(string,'""'):
            tree = ()
            for char in string_split(string[1:-1]):
                if len(char)>1 and char[0]=='\\': char = special(char[1])
                subtree = ('chr', '_', str(ord(char)))
                tree = subtree if not tree else ('+', tree, subtree)
            # TODO Is there a more robust way of making an empty string in pyramid scheme??
            if not tree: tree = ('eps',)
            return tree
        return string

    return tree_traversal(ast,str_fun=expand)

#=============================================================================================================================================
#                                                                                                                                             
#   #####   ##   ##  #####  #####  ##   ##  ##      ##             ####   #####   ###    ###  ###    ###                                    
#  ##   ##  ##   ##  ##     ##     ##   ##  ##      ##            ##     ##   ##  ## #  # ##  ## #  # ##                                    
#  ##   ##  ##   ##  #####  #####  ##   ##  ##      ##            ##     ##   ##  ##  ##  ##  ##  ##  ##                                    
#  ##   ##   ## ##   ##     ##     ##   ##  ##      ##            ##     ##   ##  ##      ##  ##      ##                                    
#   #####     ###    #####  ##      #####   ######  ######         ####   #####   ##      ##  ##      ##  ##                                
#                                                                                                                                             
#=============================================================================================================================================

@in_processing_stack
def expand_overfull_outs(ast):

    def expander(node):
        if len(node) > 3 and node[0] == 'out':
            node = (('out',*p) for p in in_pairs(node[1:],in_tuple=True))
        return node

    return tree_traversal(ast,pre_fun=expander)

binary_operators = set(('+','-','*','/','^','=','<=>'))

@in_processing_stack
def expand_left_associative(ast):

    def expander(node):
        if len(node) > 3 and node[0] in binary_operators:
            tree = node[:3]
            for element in node[3:]:
                tree = (node[0], tree, element)
            return tree
        return node

    return tree_traversal(ast,pre_fun=expander)

@in_processing_stack
def expand_right_associative(ast):

    def expander(node):
        if len(node) > 2 and node[-1] in binary_operators:
            tree = (node[-1], *node[-3:-1])
            print(tree)
            for element in reversed(node[:-3]):
                tree = (node[-1], element, tree)
            return tree
        return node

    return tree_traversal(ast,pre_fun=expander)

#=============================================================================================================
#                                                                                                             
#  #####    #####    ####  ######            #####   #####     #####    ####                                
#  ##  ##  ##   ##  ##       ##              ##  ##  ##  ##   ##   ##  ##                                   
#  #####   ##   ##   ###     ##    ########  #####   #####    ##   ##  ##                                   
#  ##      ##   ##     ##    ##              ##      ##  ##   ##   ##  ##                                   
#  ##       #####   ####     ##              ##      ##   ##   #####    ####                                
#                                                                                                             
#=============================================================================================================

## TESTED
@in_processing_stack
def expand_overfull_brackets(ast):
    ''' Expand lists of many lists into lists of length 2 '''

    def expander(node):
        if all(map(is_tuple,node)):
            while len(node)>2:
                node = tuple(p for p in in_pairs(node))
        elif len(node)>3:
            raise PsllSyntaxError(f'Invalid bracket structure. Can only expand lists of lists.')
        return node
        
    return tree_traversal(ast,post_fun=expander)

@in_processing_stack
def fill_in_empty_trees(ast):
    ''' Fill in the implicit empty strings in brackets with only lists '''
    def filler(node):
        if node == (): # Empty node
            return ('')
        elif all(map(is_tuple,node)): # All tuples
            return ('',*node)
        elif node[0] == '_':
            return ('',*node)
        elif node[0] in PS_KEYWORDS:
            return node # Don't add a pad before psll keywords
        else:
            return ('',*node) # Add pad before non-keywords (this allows one to make arrays)

    return tree_traversal(ast,post_fun=filler)

@in_processing_stack
def fill_in_underscores(ast):

    def filler(node):
        if len(node)==3:
            if is_string(node[1]) and node[1] != '_':
                node = (node[0], (node[1], '_', '_'), node[2])
            if is_string(node[2]) and node[2] != '_':
                node = (node[0], node[1], (node[2], '_', '_'))
            pass
        elif len(node)==2:
            if is_string(node[1]) and node[1] != '_':
                node = (node[0], (node[1], '_', '_'), '_')
            else:
                node = (*node,'_')
        elif len(node)==1 and node[0] != '_':
            node = (*node,'_','_')
        return node

    return tree_traversal(ast,post_fun=filler)

@in_processing_stack
def underscore_keyword(ast):

    def replacer(node):
        return None if node == '_' else node
    return tree_traversal(ast,str_fun=replacer)

#=========================================================================================
#                                                                                         
#   ####   #####   ###    ###  #####   ##  ##      #####                                
#  ##     ##   ##  ## #  # ##  ##  ##  ##  ##      ##                                   
#  ##     ##   ##  ##  ##  ##  #####   ##  ##      #####                                
#  ##     ##   ##  ##      ##  ##      ##  ##      ##                                   
#   ####   #####   ##      ##  ##      ##  ######  #####                                
#                                                                                         
#=========================================================================================

@cached(maxsize=10000)
def build_tree(ast):
    ''' Build the call tree from the leaves to the root '''

    if is_string(ast):
        return Pyramid.from_text(ast)
    elif ast is None:
        return None
    elif is_tuple(ast):
        if len(ast) != 3:
            raise RuntimeError(f'Invalid structure of the abstract syntax tree. ({ast})')
        if not is_string(ast[0]):
            raise RuntimeError(f'Invalid abstract syntax tree. The first element of each node must be a string, not a {type(ast[0])}')
        return build_tree(ast[0]) + (build_tree(ast[1]),build_tree(ast[2]))
    else:
        raise TypeError(f'Abstract syntax tree must be represented by a list (or just a string) not a {type(ast)}')

# TODO Refactor
def compile(ast):
    ''' Compile text into trees '''
    program = str(reduce(operator.add,(build_tree(a) for a in ast)))
    program = '\n'.join(line[1:].rstrip() for line in program.split('\n')) # Remove excessive whitespace
    return program

#===============================================================================================================================
#                                                                                                                               
#   #####   #####   ######  ##  ###    ###  ##   ####    ###    ######  ##   #####   ##     ##                                
#  ##   ##  ##  ##    ##    ##  ## #  # ##  ##  ##      ## ##     ##    ##  ##   ##  ####   ##                                
#  ##   ##  #####     ##    ##  ##  ##  ##  ##   ###   ##   ##    ##    ##  ##   ##  ##  ## ##                                
#  ##   ##  ##        ##    ##  ##      ##  ##     ##  #######    ##    ##  ##   ##  ##    ###                                
#   #####   ##        ##    ##  ##      ##  ##  ####   ##   ##    ##    ##   #####   ##     ##                                
#                                                                                                                               
#===============================================================================================================================

def greedy_optimisation(ast, verbose=True, max_iter=None):
    ''' Greedily insert empty trees into the abstract syntax tree '''

    def candidates(ast):
        for b,m,e in windowed_complete(ast,2): # Try all the pairs
            yield (*b,('',m[0],m[1]),*e)
        for b,m,e in windowed_complete(ast,1): # Finally try all the single pyramids
            yield (*b,('',m[0],None),*e)
            yield (*b,('',None,m[0]),*e)

    iter_count = 0
    if verbose: print('Greedy tree optimisation')
    while True:
        iter_count += 1
        if max_iter and iter_count>max_iter: break

        N = len(compile(ast))
        for candidate in candidates(ast):
            M = len(compile(candidate))
            if M < N:
                if verbose: print(f'{iter_count} | Old len: {N} | New len: {M}')
                ast = candidate
                break # Greedilly accept the new ast
        else:
            break # Break from the while loop
    return ast

def repeat(func, n, arg):
    if n < 0: raise ValueError
    if n == 0: return arg
    out = func(arg)
    for _ in range(n-1):
        out = func(out)
    return out

def considerate_optimisation(ast,verbose=True,max_iter=None,max_depth=10):
    ''' Consider all the possible places to insert a tree up to ``max_depth`` '''
    
    wrap_left = lambda node: ('',node,None) # Wrap a node
    wrap_right = lambda node: ('',None,node) # Wrap a node

    def candidates(ast):
        for b,m,e in chain(windowed_complete(ast,1),windowed_complete(ast,2)):
            m = ('',m[0],m[1]) if len(m)==2 else m[0]
            for d in range(1,max_depth):
                yield (*b,repeat(wrap_left,d,m),*e)
            for d in range(1,max_depth):
                yield (*b,repeat(wrap_right,d,m),*e)

    iter_count = 0
    if verbose: print('Considerate optimisation')
    while True:
        iter_count += 1
        if max_iter and iter_count>max_iter: break

        N = len(compile(ast))
        lengths = ((len(compile(c)),c) for c in candidates(ast))
        M, candidate = min(lengths, key=operator.itemgetter(0))
        if M < N:
            if verbose:
                print(f'{iter_count} | Old len: {N} | New len: {M}')
            ast = candidate
        else:
            break # Break from the while loop
    return ast

#======================================================================
#                                                                      
#  ###    ###    ###    ##  ##     ##                                
#  ## #  # ##   ## ##   ##  ####   ##                                
#  ##  ##  ##  ##   ##  ##  ##  ## ##                                
#  ##      ##  #######  ##  ##    ###                                
#  ##      ##  ##   ##  ##  ##     ##                                
#                                                                      
#======================================================================

def main(args): # pragma: no cover
    ''' Main function for the command-line operation '''
    if args.verbose: print('Input filename:',args.input)
    if args.output and args.verbose: print('Output filename:',args.output)
    
    text = readfile(args.input)
    if args.verbose: print('Reduced source:',text)
    
    ast = lex(text)
    print(ast,end='\n\n')
    # names = find_variable_names(ast)
    # print('variables:',variables)

    stack = __processing_stack__[1:] if args.full_names else __processing_stack__
    ast = reduce(lambda x,y: y(x), [ast] + list(stack))
    
    # TODO  Make optimisation options mutually exclusive
    if args.considerate_optimisation:
        ast = considerate_optimisation(ast, max_iter=None)
    if args.greedy_optimisation:
        ast = greedy_optimisation(ast, max_iter=None)

    program = compile(ast)
    if args.verbose: print('Pyramid scheme:', program,sep='\n')
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(program)

if __name__ == "__main__":

    import argparse
    import os.path

    def valid_input_file(filename):
        if not os.path.exists(filename):
            raise argparse.ArgumentTypeError(f'The file {filename} does not exist!')
        if os.path.splitext(filename)[1] != '.psll':
            raise argparse.ArgumentTypeError(f'The input file does not have an .psll extension!')
        return filename

    def valid_output_file(args,ext='.pyra'):
        filename = args.output
        if not filename: return # Return if no -o option
        # Make filename based on the input filename
        if filename==' ':
            filename = os.path.splitext(args.input)[0] + ext
            args.output = filename
        # Check whether to overwrite
        if os.path.exists(filename) and not args.force:
            answer = input(f'File {filename} already exists. Overwrite? [y/N]')
            if answer.lower() != 'y':
                args.output=None
        # Check extension
        if os.path.splitext(filename)[1] != ext:
            raise argparse.ArgumentTypeError(f'The output file does not have an .pyra extension!')

    parser = argparse.ArgumentParser(description='Compile lisp-like syntax to Pyramid Scheme')
    parser.add_argument('input', type=valid_input_file,
        help='Input file written in the pyramid scheme (lisp (like)) syntax, with the .psll expension.')
    parser.add_argument('-o', dest='output', required=False,
        metavar='output', nargs='?', default = None, const = ' ',
        help='Output pyramid scheme. If "output" is supplied, the pyramid scheme is saved to that filename. If no "output" is supplied (aka just the -o option) the pyramid scheme is saved to the filename matching the input filename, with the .pyra extension.')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Run in the verbose mode.')
    parser.add_argument('-f', '--force', action='store_true',
        help='Force file overwrite.')
    
    parser.add_argument('--full-names', action='store_true',
        help='Don\'t shorten variable names when compiling the pyramid scheme. This will result in longer, but potentially more readable source code. Usefull for either compiler or pyramid scheme debugging.')

    parser.add_argument('-go','--greedy-optimisation', action='store_true',
        help='Greedily insert an empty pyramid the very first place which minimised the size is beneficial. This tends to result in tall source code.')
    parser.add_argument('-co','--considerate-optimisation', action='store_true',
        help='Consider all the possible places to insert a pyramid, up to certain depth. Choose the most beneficial. This tends to result in wide source code.')

    # Compiler options
    # parser.add_argument('-nt','--null-trees', action='store_true',
    #     help='Use null (height 0) trees.')
    # parser.add_argument('--dot-spaces', action='store_true',
    #     help='Render spaces as dots')

    args = parser.parse_args()
    valid_output_file(args)

    main(args)
