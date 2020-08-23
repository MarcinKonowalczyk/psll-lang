#!/usr/bin/python3

import re
from itertools import zip_longest

from windowed_complete import windowed_complete
from itertools import chain
from functools import partial
from functools import lru_cache as cached

from tree_repr import Pyramid

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

#=====================================================================================================
#                                                                                                     
#  #####   #####    #####            #####   #####     #####    ####                                
#  ##  ##  ##  ##   ##               ##  ##  ##  ##   ##   ##  ##                                   
#  #####   #####    #####  ########  #####   #####    ##   ##  ##                                   
#  ##      ##  ##   ##               ##      ##  ##   ##   ##  ##                                   
#  ##      ##   ##  #####            ##      ##   ##   #####    ####                                
#                                                                                                     
#=====================================================================================================

def tree_traversal(ast, str_fun=None, post_fun=None, pre_fun=None,final_fun=None):
    ''' (Depth-first) walk through the abstract syntax tree and apply appropriate functions '''
    ast2 = [] # Build a new ast
    for node in ast:
        if isinstance(node,str):
            ast2.append(str_fun(node) if str_fun else node)
        elif isinstance(node,tuple):
            node = pre_fun(node) if pre_fun else node
            node = tree_traversal(node, pre_fun=pre_fun, str_fun=str_fun, post_fun=post_fun, final_fun=final_fun)
            # TODO Nicer way of passing many kwargs...? ^
            node = post_fun(node) if post_fun else node
            ast2.append(node)
        else:
            raise TypeError(f'The abstract syntax tree can contain only strings or other, smaller, trees, not {type(node)}')
    if final_fun:
        final_fun(ast2)
    return tuple(ast2) # Return ast back as a tuple

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
                raise PsllSyntaxError("Hic sunt dracones")
                # TODO ^ rename, although I find it very funny
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
    def replace_rules(node):
        if len(node)==1 and node[0] in rules.keys():
            return rules[node[0]]
        return node
    ast = tree_traversal(ast,post_fun=replace_rules)

    def replace_rules(node):
        if node in rules.keys():
            return rules[node]
        return node
    ast = tree_traversal(ast,str_fun=replace_rules)

    return ast

def expand_sting_literals(ast):
    ''' Expand all the psll string literals objects into pyramid scheme trees '''
    
    def expand(string):
        if re.match('(\'.+\'|".+")',string):
            tree = ()
            for character in string[1:-1]:
                subtree = ('chr', str(ord(character)))
                tree = subtree if not tree else ('+', tree, subtree)
            return tree
        elif re.match('(\'\'|"")',string):
            # TODO Is there a more robust way of making an empty string in pyramid scheme??
            return ('eps',) # 'eps' is an empty string
        else:
            return string

    return tree_traversal(ast,str_fun=expand)

def pair_up(iterable):
    ''' Pair up elements in the array. (s1,s2,s3,s4,s5) -> ((s1,s2),(s3,s4),s5) '''
    args = [iter(iterable)] * 2
    for j,k in zip_longest(*args, fillvalue=None):
        value = (j,k) if k else j
        yield value

def expand_overfull_brackets(ast):
    ''' Recursively expand lists of many lists into lists of length 2 '''

    def expander(node):
        if all(map(lambda x: isinstance(x,tuple),node)):
            while len(node)>2:
                node = tuple(p for p in pair_up(node))
        elif len(node)>3:
            raise PsllSyntaxError(f'Invalid bracket structure. Can only expand lists of lists. Node = \'{node}\'')
        return node
        
    return tree_traversal(ast,post_fun=expander)

def fill_in_empty_trees(ast):
    ''' Fill in the implicit empty strings in brackets with only lists '''
    
    def filler(node):
        if node:
            if not isinstance(node[0],str):
                node = ('',*node)
        else:
            node = ('',)
        return node

    return tree_traversal(ast,post_fun=filler)

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
    
    elif isinstance(ast,tuple):
        if not len(ast)>0:
            raise AssertionError('Invalid abstract syntax tree. Abstract syntax tree cannot be empty')
        if not isinstance(ast[0],str):
            raise AssertionError(f'Invalid abstract syntax tree. The first element of each node must be a string, not a {type(ast[0])}')

        if len(ast)==1:
            tree = build_tree(ast[0])

        elif len(ast)==2:
            # TODO Choice (left/right) trees...?
            root = build_tree(ast[0])
            left_leaf = build_tree(ast[1])
            tree = root + (left_leaf,None)

        elif len(ast)==3:
            root = build_tree(ast[0])
            left_leaf = build_tree(ast[1])
            right_leaf = build_tree(ast[2])
            tree = root + (left_leaf,right_leaf)

        else:
            raise PsllSyntaxError('Invalid number of input arguments')
    else:
        raise TypeError(f'Abstract syntax tree must be represented by a list (or just a string) not a {type(ast)}')
    return tree

#=========================================================================================
#                                                                                         
#   ####   #####   ###    ###  #####   ##  ##      #####                                
#  ##     ##   ##  ## #  # ##  ##  ##  ##  ##      ##                                   
#  ##     ##   ##  ##  ##  ##  #####   ##  ##      #####                                
#  ##     ##   ##  ##      ##  ##      ##  ##      ##                                   
#   ####   #####   ##      ##  ##      ##  ######  #####                                
#                                                                                         
#=========================================================================================

def compile(ast):
    ''' Compile text into trees '''    
    # Pre-process
    # print('Raw:\n',ast,end='\n\n')
    # print('Def-replacement:\n',ast,end='\n\n')
    ast = expand_sting_literals(ast)
    ast = expand_overfull_brackets(ast)
    ast = fill_in_empty_trees(ast)
    # print('End of pre-proc:\n',ast,end='\n\n')

    # Build
    trees = [build_tree(a) for a in ast]
    program = trees[0]
    for tree in trees[1:]:
        program += tree

    # Post-process
    program = str(program)
    program = '\n'.join(line[1:].rstrip() for line in program.split('\n'))

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
    
    every_partition = lambda seq: chain(*map(
        partial(windowed_complete,seq),range(2,len(seq))))

    iter_count = 0
    if verbose: print('Greedy tree optimisation')
    while True:
        iter_count += 1
        if max_iter and iter_count>max_iter:
            break

        N = len(compile(ast))
        for pre,hay,suf in every_partition(ast):
            # TODO Find a non-hacky way to do this
            new_ast = (*pre,tuple(x for x in hay),*suf)
            M = len(compile(new_ast))
            if M < N:
                if verbose: print(f'{iter_count} | Old len: {N} | New len: {M}')
                ast = new_ast
                break # Accept the new ast
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

def singleton_optimisation(ast,verbose=True,max_iter=None):
    '''  '''

    # TODO Work In Progress
    
    iter_count = 0
    if verbose: print('Singleton optimisation')
    while True:
        iter_count += 1
        if max_iter and iter_count>max_iter:
            break
        
        N = len(compile(ast))
        new_asts = []
        for pre,hay,suf in chain(windowed_complete(ast,1),windowed_complete(ast,2)):
            for d in range(1,20+1): # Add up to 5 levels of pyramids
                new_hay = repeat(lambda x: (x,),d,(hay))
                new_ast = (*pre,tuple(x for x in new_hay),*suf)
                new_asts.append(new_ast)
        lengths = list(len(compile(a)) for a in new_asts)
        print('len:',len(lengths))
        M, I = min((v,i) for (i,v) in enumerate(lengths))
        if M < N:
            if verbose:
                print(f'{iter_count} | Old len: {N} | New len: {M} | Insert: {I+1}')
            ast = new_asts[I]
            # break # Accept the new ast
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
    ast = def_keyword(ast)
    # TODO ^ find better place
    if args.singleton_optimisation:
        ast = singleton_optimisation(ast,max_iter=None)
    if args.greedy_optimisation:
        ast = greedy_optimisation(ast,max_iter=None)

    program = compile(ast)
    if args.verbose: print('Pyramid scheme:',program,sep='\n')
    
    if args.output:
        with open(args.output,'w') as f:
            f.write(program)

if False: #__name__ == "__main__":
    import argparse
    args = argparse.Namespace(
        greedy_optimisation=False,
        singleton_optimisation=False,
        input='./examples/def_keyword.psll',
        output='./examples/def_keyword.pyra',
        force=True,
        verbose=False
        )
    main(args)
    print('done')

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
    
    parser.add_argument('-go','--greedy-optimisation', action='store_true',
        help='Minimise the size of the resulting code by attempting blank pyramid inserts. This is a greedy strategy which inserts the pyramid at the very first place it finds which is beneficial. This tends to result in tall source code.')
    parser.add_argument('-so','--singleton-optimisation', action='store_true',
        help='Experimental')
    # Compiler options
    # parser.add_argument('-nt','--null-trees', action='store_true',
    #     help='Use null (height 0) trees.')
    # parser.add_argument('--dot-spaces', action='store_true',
    #     help='Render spaces as dots')

    args = parser.parse_args()
    valid_output_file(args)

    # print(args)
    main(args)
