#!/usr/bin/python3

import re
from itertools import zip_longest

from tree_repr import Pyramid

SPACE = ' '

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

def split_into_trees(text):
    ''' Split the text into major trees '''
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

    return lines

def split_into_subtrees(line):
    ''' Split each tree into subtrees '''
    if re.match('\(.*\)',line): # Remove outermost bracket
        line = line[1:-1];
    line += ' '

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
        if char == ' ' and bracket_count == 0 and not last_quote:
            part = line[last_break:j]
            tree.append(part)
            last_break = j+1
    
    # Recursively split parts of self 
    tree = [split_into_subtrees(subtree) if re.match('\(.*\)',subtree) else subtree for subtree in tree]

    return tree

#=====================================================================================================
#                                                                                                     
#  #####   #####    #####            #####   #####     #####    ####                                
#  ##  ##  ##  ##   ##               ##  ##  ##  ##   ##   ##  ##                                   
#  #####   #####    #####  ########  #####   #####    ##   ##  ##                                   
#  ##      ##  ##   ##               ##      ##  ##   ##   ##  ##                                   
#  ##      ##   ##  #####            ##      ##   ##   #####    ####                                
#                                                                                                     
#=====================================================================================================

def pair_up(iterable):
    ''' Pair up elements in the array '''
    args = [iter(iterable)] * 2
    for j,k in zip_longest(*args, fillvalue=None):
        value = [j,k] if k else j
        yield value

def is_psll_string(x):
    ''' Check whether x is a psll string '''
    if not isinstance(x,str):
        return false # Is a tree
    return re.match('(\'.*\'|".*")',x)

def expand_string_to_tree(string):
    ''' Expand psll string to an appropriate tree '''
    tree = [];
    for character in string[1:-1]:
        subtree = ['chr', str(ord(character))]
        if not tree:
            tree = subtree
        else:
            tree = ['+', tree, subtree]
    return tree

def expand_all_stings(ast):
    ''' Walk through the abstract syntax tree and expand all the psll string objects into pyramid scheme trees '''
    ast2 = []
    for node in ast:
        if isinstance(node,str):
            if is_psll_string(node):
                ast2.append(expand_string_to_tree(node))
            else:
                ast2.append(node)
        elif isinstance(node,list):
            ast2.append(expand_all_stings(node))
        else:
            raise TypeError
    return ast2

#=======================================================================
#                                                                       
#  #####   ##   ##  ##  ##      ####                                  
#  ##  ##  ##   ##  ##  ##      ##  ##                                
#  #####   ##   ##  ##  ##      ##  ##                                
#  ##  ##  ##   ##  ##  ##      ##  ##                                
#  #####    #####   ##  ######  ####                                  
#                                                                       
#=======================================================================


def build_tree(ast,**kwargs):
    ''' Build the call tree from the leaves to the root '''

    if not isinstance(ast,list):
        print(ast)
    # Not PsllSyntaxErrors. These should not happen normally
    assert isinstance(ast,list), f'Abstract syntax tree must be a list, not a {type(ast)}'
    assert len(ast)>0, 'Abstract syntax tree cannot be empty'

    # TODO Code these a bit more sanely
    null_trees = kwargs['null_trees'] if 'null_trees' in kwargs else False

    # Add the null tree if none specified
    # TODO Move this to pre-processor
    pad_tree = '' if null_trees else ' '
    if not isinstance(ast[0],str) and len(ast) < 3:
        ast = [pad_tree] + ast

    if isinstance(ast[0],str):
        if len(ast)==1:
            # TODO Move this to pre-processor
            if ast[0]=='' and not null_trees: ast[0] = ' ' # Make sure no null-trees
            tree = Pyramid.from_text(ast[0])

        elif len(ast)==2:
            root = Pyramid.from_text(ast[0])
            left_leaf = Pyramid.from_text(ast[1]) if isinstance(ast[1],str) else build_tree(ast[1],**kwargs)
            tree = root + (left_leaf,None)

        elif len(ast)==3:
            root = Pyramid.from_text(ast[0])
            left_leaf = Pyramid.from_text(ast[1]) if isinstance(ast[1],str) else build_tree(ast[1],**kwargs)
            right_leaf = Pyramid.from_text(ast[2]) if isinstance(ast[2],str) else build_tree(ast[2],**kwargs)
            tree = root + (left_leaf,right_leaf)

        else:
            raise PsllSyntaxError('Invalid number of input arguments')
    else: # The first element of a tree is *not* string but a tree
        if len(ast) == 1:
            tree =  build_tree(ast[0],**kwargs)
        else:
            # TODO Move this to pre-processor
            while len(ast)>2:
                ast = [p for p in pair_up(ast)]
            ast = [pad_tree] + ast
            tree = build_tree(ast,**kwargs)

    return tree

def combine_trees(trees,space='.'):
    ''' Put multiple trees side by side '''
    while len(trees)>1:
        tree_left = trees[0].split('\n')
        tree_right = trees[1].split('\n')

        fillvalue = space*len(tree_left[0]) if len(tree_left)<len(tree_right) else space*len(tree_right[0])
        combined = [l+r for l,r in zip_longest(tree_left,tree_right,fillvalue=fillvalue)]

        combined = ['\n'.join(combined)]
        trees = combined + trees[2:]
    return trees[0]

#=========================================================================================
#                                                                                         
#   ####   #####   ###    ###  #####   ##  ##      #####                                
#  ##     ##   ##  ## #  # ##  ##  ##  ##  ##      ##                                   
#  ##     ##   ##  ##  ##  ##  #####   ##  ##      #####                                
#  ##     ##   ##  ##      ##  ##      ##  ##      ##                                   
#   ####   #####   ##      ##  ##      ##  ######  #####                                
#                                                                                         
#=========================================================================================

def compile(text,space=' ',null_trees=False):
    ''' Compile text into trees '''
    # Lex
    trees = split_into_trees(text)
    asts = [split_into_subtrees(tree) for tree in trees]
    
    # Pre-process
    asts = expand_all_stings(asts) # Expans psll strings
    
    # Build
    trees = [build_tree(ast,null_trees=null_trees) for ast in asts]
    program = trees[0]
    for tree in trees[1:]:
        program += tree

    # Post-processing
    program = str(program)
    program = '\n'.join(re.sub('\s*(?=$)','',line[1:]) for line in program.split('\n'))
    # Regex '^(.*?)\s*$' would probably work too

    return program

def main(args):
    ''' Main function for the command-line operation '''

    verbose = args.verbose
    input = args.input
    output = args.output

    if verbose: print('Input filename:',input)
    if output and verbose:
        print('Output filename:',output)
    
    text = readfile(input)
    if verbose: print('Reduced source:',text)
    
    space = '.' if args.dot_spaces else ' '
    program = compile(text,space=space,null_trees=args.null_trees)

    if verbose: print('Pyramid scheme:',program,sep='\n')
    
    if output:
        with open(output,'w') as f:
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
        help='Output pyramid scheme. If "output" is supplied, the pyramid scheme is saved to that filename. If no "output" is supplied (aka just the  -o option) the pyramid scheme is saved to the filename matching the input filename, with the .pyra extension.')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Run in the verbose mode.')
    parser.add_argument('-f', '--force', action='store_true',
        help='Force file overwrite.')
    parser.add_argument('--null-trees', action='store_true',
        help='Use null (height 0) trees.')
    parser.add_argument('--no-compact', action='store_true',
        help="Don't compact the output trees")
    parser.add_argument('--dot-spaces', action='store_true',
        help='Render spaces as dots')

    args = parser.parse_args()
    valid_output_file(args)

    main(args)
