#!/usr/bin/python3

import re
from itertools import zip_longest, chain

from functools import partial, reduce
from functools import lru_cache as cached
import operator
from string import ascii_letters

from windowed_complete import windowed_complete
from ascii_trees import Pyramid

SPACE = ' '

# TODO Test depth
def depth(tree):
    ''' Calculate the depth of a tree '''
    if isinstance(tree,str):
        return 0
    elif isinstance(tree,tuple):
        if len(tree)==0:
            return 0
        else:
            return max(depth(node) for node in tree) + 1
    else:
        raise TypeError(f'The abstract syntax tree can contain only strings or other, smaller, trees, not {type(tree).__name__}')

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
    '''
    Read the file, remove comments and make sure all the lines are
    in correct brackets
    '''

    with open(filename,'r') as f:
        text = f.read()

    subs = ((r'//.*',''), # Remove comments
        (r'\s{1,}',' '), # Only single spaces
        (r'((?<=^)\s+|\s+(?=$))',''), # No trailing or leading whitespace
        (r'((?<=\()\s+|\s+(?=\)))',''), # Spaces inside brackets
        (r'(?<=\))(?=\()',' ')) # Put single spaces between crammed brackets
    # Apply substitutions
    for a,b in subs:
        text = re.sub(a,b,text)

    return text

#=============================================================
#                                                             
#  ##      #####  ##    ##                                    
#  ##      ##      ##  ##                                     
#  ##      #####    ####                                      
#  ##      ##      ##  ##                                     
#  ######  #####  ##    ##                                    
#                                                             
#=============================================================

@cached(maxsize=1000)
def split_into_lines(text):
    ''' Split the reduced source into 1st-level brackets (aka major trees) '''
    # Split into lines at first level brackets
    count, last_count, last_break = (0,0,0)
    lines = []
    for j,char in enumerate(text):
        count += 1 if char=='(' else 0
        count -= 1 if char==')' else 0
        if count == 0: # End of a bracket
            if last_count != 0:
                line = text[last_break:(j+1)]
                lines.append(line)
            else: # Start of a new bracket
                last_break = j+1
        elif count < 0:
            raise PsllSyntaxError('Invalid bracket alignment (ketbra)')
        last_count = count

    if count != 0: # Check the final count is 0
        raise PsllSyntaxError('Invalid bracket parity.')

    return tuple(lines)

def split_into_subtrees(line):
    ''' Split each tree into subtrees '''
    if re.match('\(.*\)',line): # Remove outermost bracket
        line = line[1:-1];
    line += SPACE

    bracket_count, last_break = (0,0) # Kepping track of bracket parity
    last_quote = '' # Keeping track of quotation marks

    tree = []
    for j,char in enumerate(line):
        bracket_count += 1 if char=='(' else 0
        bracket_count -= 1 if char==')' else 0
        for quote in ['"','\'']:
            if char==quote:
                if not last_quote: last_quote = quote # Start a quote
                elif last_quote==quote: last_quote = '' # End a quote

        # Break at spaces, but not in the middle of brackets of strings
        if char == SPACE and bracket_count == 0 and not last_quote:
            part = line[last_break:j]
            tree.append(part)
            last_break = j+1
    
    # Recursively split parts of self 
    return tuple(split_into_subtrees(subtree) if re.match('\(.*\)',subtree) else subtree for subtree in tree)

def lex(text):
    ''' Compose a basic abstract syntax tree from the reduced source '''
    ast = tuple(split_into_subtrees(line) for line in split_into_lines(text))
    return ast

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
    ast2 = [] # Build a new ast
    for node in ast:
        if node is None:
            ast2.append(node)
        elif isinstance(node,str):
            ast2.append(str_fun(node) if str_fun else node)
        elif isinstance(node,tuple):
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

#=====================================================================================================
#                                                                                                     
#  #####   #####    #####            #####   #####     #####    ####                                
#  ##  ##  ##  ##   ##               ##  ##  ##  ##   ##   ##  ##                                   
#  #####   #####    #####  ########  #####   #####    ##   ##  ##                                   
#  ##      ##  ##   ##               ##      ##  ##   ##   ##  ##                                   
#  ##      ##   ##  #####            ##      ##   ##   #####    ####                                
#                                                                                                     
#=====================================================================================================

def find_variable_names(ast):
    ''' Find all the variable names used in the code '''
    names = set()
    def variable_finder(node):
        if len(node)==3:
            if node[0] == 'set' and isinstance(node[1],str):
                names.add(node[1])
    tree_traversal(ast,post_fun=variable_finder)
    return names

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

        
def def_keyword(ast):
    ''' Search for ('def','something',(...)) keywords '''

    defs = []
    def replacer(node):
        if len(defs)>0:
            for b,m,e in windowed_complete(reversed(defs),1):
                value,definition = m[0]
                if node==value: # Node needs to be replaced
                    return definition
        return node

    def find_defs(node):
        if len(node)>0 and node[0]=='def':
            if not len(node)==3:
                raise PsllSyntaxError(f"'def' statement must have 3 members, not {len(node)} (node = {node})")
            if not isinstance(node[1],str) or not isinstance(node[2],tuple):
                raise PsllSyntaxError(f"'def' statement can only assign brackets to values, not {type(node[2])} to {type(node[1])}")
            if node[1]=='def':
                raise PsllSyntaxError(f"('def' 'def' (...)) structure is not allowed")
            defs.append([node[1],apply_replacement_rules(node[2],dict(defs))])
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

def apply_replacement_rules(ast,rules):
    ''' Apply replacement rules to the abstract syntax tree '''
    def singleton_tuple_replacer(node): #  Replace (f) by def of f
        return rules[node[0]] if len(node)==1 and node[0] in rules.keys() else node
    def string_replacer(node): #  Replace f by def of f
        return rules[node] if node in rules.keys() else node

    return tree_traversal(ast,
        pre_fun=singleton_tuple_replacer,
        str_fun=string_replacer)

## TESTED
def expand_sting_literals(ast):
    ''' Expand all the psll string literals objects into pyramid scheme trees '''
    
    def expand(string):
        if re.match('(\'.+\'|".+")',string):
            tree = ()
            for character in string[1:-1]:
                subtree = ('chr', '_', str(ord(character)))
                tree = subtree if not tree else ('+', tree, subtree)
            return tree
        elif re.match('(\'\'|"")',string):
            # TODO Is there a more robust way of making an empty string in pyramid scheme??
            return ('eps',) # 'eps' is an empty string
        else:
            return string

    return tree_traversal(ast,str_fun=expand)

## TESTED
def expand_overfull_brackets(ast):
    ''' Recursively expand lists of many lists into lists of length 2 '''

    def pair_up(iterable):
        ''' Pair up elements in the array. (s1,s2,s3,s4,s5) -> ((s1,s2),(s3,s4),s5) '''
        args = [iter(iterable)] * 2
        for j,k in zip_longest(*args, fillvalue=None):
            value = (j,k) if k else j
            yield value
        
    def expander(node):
        if all(map(lambda x: isinstance(x,tuple),node)):
            while len(node)>2:
                node = tuple(p for p in pair_up(node))
        elif len(node)>3:
            raise PsllSyntaxError(f'Invalid bracket structure. Can only expand lists of lists.')
        return node
        
    return tree_traversal(ast,post_fun=expander)

def fill_in_empty_trees(ast):
    ''' Fill in the implicit empty strings in brackets with only lists '''
    def filler(node):
        if node:
            if not isinstance(node[0],str):
                node = ('',*node)
        else:
            node = ('')
        return node

    return tree_traversal(ast,post_fun=filler)

def fill_in_underscores(ast):
    def filler(node):
        if len(node)==3:
            if isinstance(node[1],str) and node[1] is not '_':
                node = (node[0], (node[1], '_', '_'), node[2])
            if isinstance(node[2],str) and node[2] is not '_':
                node = (node[0], node[1], (node[2], '_', '_'))
            pass
        elif len(node)==2:
            if isinstance(node[1],str) and node[1] is not '_':
                node = (node[0], (node[1], '_', '_'), '_')
            else:
                node = (*node,'_')
        elif len(node)==1 and node[0] is not '_':
            node = (*node,'_','_')
        return node
    return tree_traversal(ast,post_fun=filler)

def underscore_keyword(ast):
    def replacer(node):
        return None if node is '_' else node
    return tree_traversal(ast,str_fun=replacer)

#=======================================================================
#                                                                       
#  #####   ##   ##  ##  ##      ####                                  
#  ##  ##  ##   ##  ##  ##      ##  ##                                
#  #####   ##   ##  ##  ##      ##  ##                                
#  ##  ##  ##   ##  ##  ##      ##  ##                                
#  #####    #####   ##  ######  ####                                  
#                                                                       
#=======================================================================

@cached(maxsize=10000)
def build_tree(ast):
    ''' Build the call tree from the leaves to the root '''

    if isinstance(ast,str):
        return Pyramid.from_text(ast)
    elif ast is None:
        return None
    elif isinstance(ast,tuple):
        if len(ast) != 3:
            raise RuntimeError(f'Invalid structure of the abstract syntax tree. ({ast})')
        if not isinstance(ast[0],str):
            raise RuntimeError(f'Invalid abstract syntax tree. The first element of each node must be a string, not a {type(ast[0])}')
        return build_tree(ast[0]) + (build_tree(ast[1]),build_tree(ast[2]))
    else:
        raise TypeError(f'Abstract syntax tree must be represented by a list (or just a string) not a {type(ast)}')

#=========================================================================================
#                                                                                         
#   ####   #####   ###    ###  #####   ##  ##      #####                                
#  ##     ##   ##  ## #  # ##  ##  ##  ##  ##      ##                                   
#  ##     ##   ##  ##  ##  ##  #####   ##  ##      #####                                
#  ##     ##   ##  ##      ##  ##      ##  ##      ##                                   
#   ####   #####   ##      ##  ##      ##  ######  #####                                
#                                                                                         
#=========================================================================================

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
        for b,m,e in windowed_complete(ast,2):
            yield (*b,('',m[0],m[1]),*e)

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

def considerate_optimisation(ast,verbose=True,max_iter=None,max_depth=10):
    ''' Consider all the possible places to insert a tree up to ``max_depth`` '''

    def repeat(func, n, arg):
        if n < 0: raise ValueError
        if n == 0: return arg
        out = func(arg)
        for _ in range(n-1):
            out = func(out)
        return out
    
    wrap = lambda node: ('',node,None) # Wrap a node

    def candidates(ast):
        for b,m,e in chain(windowed_complete(ast,1),windowed_complete(ast,2)):
            m = ('',m[0],m[1]) if len(m)==2 else wrap(m[0]) # Wrap in a node
            for d in range(max_depth):
                yield (*b,repeat(wrap,d,m),*e)

    iter_count = 0
    if verbose: print('Considerate optimisation')
    while True:
        iter_count += 1
        if max_iter and iter_count>max_iter: break

        N = len(compile(ast))
        M, candidate = min( (len(compile(c)),c) for c in candidates(ast) )
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

def main(args):
    ''' Main function for the command-line operation '''
    if args.verbose: print('Input filename:',args.input)
    if args.output and args.verbose: print('Output filename:',args.output)
    
    text = readfile(args.input)
    if args.verbose: print('Reduced source:',text)
    
    ast = lex(text)
    
    # names = find_ariable_names(ast)
    # print('variables:',variables)

    stack = [ # Pre-processing function stack
        shorten_variable_names,
        def_keyword,
        expand_sting_literals,
        expand_overfull_brackets,
        fill_in_empty_trees,
        fill_in_underscores,
        underscore_keyword]
    if args.full_names:
        stack = stack[1:]
    ast = reduce(lambda x,y: y(x),[ast] + stack)
    
    # TODO  Make optimisation options mutually exclusive
    if args.considerate_optimisation:
        ast = considerate_optimisation(ast,max_iter=None)
    if args.greedy_optimisation:
        ast = greedy_optimisation(ast,max_iter=None)

    program = compile(ast)
    if args.verbose: print('Pyramid scheme:',program,sep='\n')
    
    if args.output:
        with open(args.output,'w') as f:
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
        help='Greedilly insert an empty pyramid the very first place which minimised the size is beneficial. This tends to result in tall source code.')
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
