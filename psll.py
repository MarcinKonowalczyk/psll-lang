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

def tree_traversal(ast, str_fun=None, list_fun=None):
    ''' Walk through the abstract syntax tree and apply appropriate functions '''
    ast2 = []
    for node in ast:
        if isinstance(node,str):
            ast2.append(str_fun(node) if str_fun else node)
        elif isinstance(node,list):
            node = tree_traversal(node, str_fun=str_fun, list_fun=list_fun)
            ast2.append(list_fun(node) if list_fun else node)
        else:
            raise TypeError
    return ast2

def expand_sting_literals(ast):
    ''' Expand all the psll string literals objects into pyramid scheme trees '''
    
    def expand(string):
        if re.match('(\'.*\'|".*")',string):
            tree = []
            for character in string[1:-1]:
                subtree = ['chr', str(ord(character))]
                tree = subtree if not tree else ['+', tree, subtree]
            return tree
        else:
            return string

    return tree_traversal(ast,str_fun=expand)

def pair_up(iterable):
    ''' Pair up elements in the array '''
    args = [iter(iterable)] * 2
    for j,k in zip_longest(*args, fillvalue=None):
        value = [j,k] if k else j
        yield value

def expand_overfull_brackets(ast):
    ''' Recursively expand lists of many lists into lists of length 2 '''

    def expander(node):
        if all(map(lambda x: isinstance(x,list),node)):
            while len(node)>2:
                node = [p for p in pair_up(node)]
        elif len(node)>3:
            raise PsllSyntaxError(f'Invalid bracket structure. Can only expand lists of lists. Node = \'{node}\'')
        return node
        
    return tree_traversal(ast,list_fun=expander)

def fill_in_empty_trees(ast):
    ''' Fill in the implicit empty strings in brackets with only lists '''
    ast2 = []
    for node in ast:
        if isinstance(node,str):
            ast2.append(node)
        elif isinstance(node,list):
            node = fill_in_empty_trees(node)
            if not isinstance(node[0],str):
                node = [''] + node
            ast2.append(node)
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

def build_tree(ast):
    ''' Build the call tree from the leaves to the root '''

    if isinstance(ast,str):
        return Pyramid.from_text(ast)
    
    elif isinstance(ast,list):
        assert len(ast)>0, 'Invalid abstract syntax tree. Abstract syntax tree cannot be empty'
        assert isinstance(ast[0],str), 'Invalid abstract syntax tree. The first element of each node must be a string.'

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

def compile(text):
    ''' Compile text into trees '''
    # Lex
    trees = split_into_trees(text)
    ast = [split_into_subtrees(tree) for tree in trees]
    
    # Pre-process
    ast = expand_sting_literals(ast)
    ast = expand_overfull_brackets(ast)
    ast = fill_in_empty_trees(ast)

    # Build
    trees = [build_tree(a) for a in ast]
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
    if args.verbose: print('Input filename:',args.input)
    if args.output and args.verbose: print('Output filename:',args.output)
    
    text = readfile(args.input)
    if args.verbose: print('Reduced source:',text)
    
    program = compile(text)
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
        help='Output pyramid scheme. If "output" is supplied, the pyramid scheme is saved to that filename. If no "output" is supplied (aka just the  -o option) the pyramid scheme is saved to the filename matching the input filename, with the .pyra extension.')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Run in the verbose mode.')
    parser.add_argument('-f', '--force', action='store_true',
        help='Force file overwrite.')
    
    # Compiler options
    # parser.add_argument('-nt','--null-trees', action='store_true',
    #     help='Use null (height 0) trees.')
    # parser.add_argument('-nc','--no-compact', action='store_true',
    #     help="Don't compact the output trees")
    # parser.add_argument('--dot-spaces', action='store_true',
    #     help='Render spaces as dots')

    args = parser.parse_args()
    valid_output_file(args)

    main(args)
