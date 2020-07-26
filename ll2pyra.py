#!/usr/bin/python3

import re
from itertools import zip_longest

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
    
def split_into_trees(text):
    '''
    Split the text into major trees
    '''
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
        last_count = count

    if count != 0: # Check the final count is 0
        raise SyntaxError(f'Bracket parity error')

    return lines

def split_into_subtrees(line):
    '''
    Split tree into subtrees
    '''
    if re.match('\(.*\)',line): # Remove outermost bracket
        line = line[1:-1];
    line += ' '

    count, last_break = (0,0)
    tree = []
    for j,char in enumerate(line):
        count += 1 if char=='(' else 0
        count -= 1 if char==')' else 0
        if char == ' ' and count == 0:
            part = line[last_break:j]
            tree.append(part)
            last_break = j+1
    
    # Recursively split parts of self 
    tree = [split_into_subtrees(subtree) if re.match('\(.*\)',subtree) else subtree for subtree in tree]

    return tree

def text_to_pyramid(text,min_len=0,space='.'):
    '''
    Put text in a pyramid
    '''
    # Pad up to length
    if text or min_len > 0:
        text = text.replace(' ','') # Remove excessive whitespace
        N = max(len(text),min_len)
        level = N//2
        pad_length = level*2+1-len(text)
        text = space*((pad_length//2)) + text + space*(pad_length-(pad_length//2))

        # Make the pyramid
        pyramid = space*(level+1) + '^' + space*(level+1) + '\n'
        for j in range(level):
            pyramid += space*(level-j) + '/' + space*(j*2+1) + '\\' + space*(level-j) + '\n'
        pyramid += '/' + text + '\\\n'
        pyramid += space*0 + '-'*(2*level+3) + space*0
    
    else:
        pyramid = '^\n-' # Null pyramid
    
    return pyramid

def build_tree_bottom_up(tree,**kwargs):
    '''
    Build the call tree from the leaves to the root
    '''

    assert isinstance(tree,list), f'Tree must be a list ({tree})'
    space = kwargs['space']
    null_trees = kwargs['null_trees']

    # Add the null tree if none specified
    pad_tree = '' if null_trees else ' '
    if not isinstance(tree[0],str):
        tree = [pad_tree] + tree

    if len(tree)==1:
        if isinstance(tree[0],str):
            return text_to_pyramid(tree[0],space=space)
        else:
            return build_tree_bottom_up(tree[0],**kwargs)
    elif len(tree)==2:
        root = text_to_pyramid(tree[0],space=space).split('\n')
        if isinstance(tree[1],str):
            left_leaf = text_to_pyramid(tree[1],space=space)
        else:
            left_leaf = build_tree_bottom_up(tree[1],**kwargs)
        left_leaf = left_leaf.split('\n')

        # Find apex of left leaf
        root_pad = left_leaf[0].find('^')+1

        # Stitch together
        root = [space*root_pad + row for row in root]
        root[-1] = re.sub(f'{re.escape(space)}(?=-+)','^',root[-1]) # Add the peak of the leaf to the last row root
        
        # for line in root: print(line)    
        # for line in left_leaf: print(line)

        tree = root + left_leaf[1:]
        tree_width = max(len(l) for l in tree)
        tree = [line + (tree_width-len(line))*space for line in tree]

        tree = '\n'.join(tree)

    elif len(tree)==3:
        if isinstance(tree[1],str):
            left_leaf = text_to_pyramid(tree[1],space=space)
        else:
            left_leaf = build_tree_bottom_up(tree[1],**kwargs)
        left_leaf = left_leaf.split('\n')
        
        if isinstance(tree[2],str):
            right_leaf = text_to_pyramid(tree[2],space=space)
        else:
            right_leaf = build_tree_bottom_up(tree[2],**kwargs)
        right_leaf = right_leaf.split('\n')

        right_spaces = lambda x: len(x)-x.rfind('^')-1;
        left_spaces = lambda x: x.find('^');

        spacing = right_spaces(left_leaf[0]) + left_spaces(right_leaf[0])
        middle_pad = space*((spacing+1)%2)
        spacing = spacing + ((spacing+1)%2)
        
        root = text_to_pyramid(tree[0],min_len=spacing-2,space=space).split('\n')

        # Check the root does not actually need to be bigger
        len_root = len(root[-1])
        if len_root>spacing:
            middle_pad += space*(len_root-spacing)
            spacing = len_root

        # Put children together
        fillvalue = space*len(left_leaf[0]) if len(left_leaf)<len(right_leaf) else space*len(right_leaf[0])
        children = [l+middle_pad+r for l,r in zip_longest(left_leaf,right_leaf,fillvalue=fillvalue)]
        # for line in left_leaf: print(line)
        # for line in children: print(line)

        left_peak = children[0].find('^')
        right_peak = children[0].rfind('^')

        # Pad the root
        root = [space*(left_peak+1) + row for row in root]
        # Add bottom rung of the root between the peaks of the children
        children[0] = children[0][:left_peak+1] + '-'*(right_peak-left_peak-1) + children[0][right_peak:]

        tree = root[:-1] + children
        tree_width = max(len(l) for l in tree)
        tree = [line + (tree_width-len(line))*space for line in tree]

        tree = '\n'.join(tree)

    else:
        raise SyntaxError('Invalid number of input arguments')

    return tree

def combine_trees(trees,space='.'):
    '''
    Put multiple trees side by side
    '''
    while len(trees)>1:
        tree_left = trees[0].split('\n')
        tree_right = trees[1].split('\n')

        fillvalue = space*len(tree_left[0]) if len(tree_left)<len(tree_right) else space*len(tree_right[0])
        combined = [l+r for l,r in zip_longest(tree_left,tree_right,fillvalue=fillvalue)]

        combined = ['\n'.join(combined)]
        trees = combined + trees[2:]
    return trees[0]

def compile(text,space=' ',null_trees=False):
    '''
    Compile text into trees
    '''
    trees = split_into_trees(text)
    trees = [split_into_subtrees(tree) for tree in trees]
    
    build = lambda tree: build_tree_bottom_up(tree,space=space,null_trees=null_trees)
    trees = [build(tree) for tree in trees]
    
    trees = combine_trees(trees,space=space)
    return trees

def compact(trees):
    '''
    Compact the trees
    '''
    trees = trees.split('\n')
    
    def remove_empty_columns(trees):
        trees = [list(j) for j in zip_longest(*trees,fillvalue=' ')]
        isempty = lambda line: all(entry==' ' for entry in line)
        trees2 = []
        started, previous_empty = (False, False)
        for j,line in enumerate(trees):
            if isempty(line):
                if not started:
                    trees2.append(line)
                elif not previous_empty:
                    trees2.append(line) # WIP <- check whether this line cannot be sometimes gotten rid of
                previous_empty = True
            else:
                started = True
                previous_empty = False
                trees2.append(line)
        return [''.join(j) for j in zip(*trees2)]

    trees = [j*' ' + line for j,line in enumerate(trees)]
    trees = remove_empty_columns(trees)
    trees = [line[j:] for j,line in enumerate(trees)]
    

    trees = [(len(trees)-j-1)*' ' + line for j,line in enumerate(trees)]
    trees = remove_empty_columns(trees)
    trees = [line[(len(trees)-j-1):] for j,line in enumerate(trees)]

    trees = [re.sub('\s+(?=$)','',line) for line in trees] # Remove trailing whitespace

    return '\n'.join(trees)


def main(args):
    '''
    Main function for the command-line operation
    '''

    verbose = args.verbose
    input = args.input
    output = args.output

    if verbose: print('Input filename:',input)
    if output and verbose:
        print('Output filename:',output)
    
    text = readfile(input)
    if verbose: print('Reduced source:',text)
    
    space = '.' if args.dot_spaces else ' '
    trees = compile(text,space=space,null_trees=args.null_trees)
    if not args.no_compact:
        trees = compact(trees)

    if verbose: print('Pyramid scheme:',trees,sep='\n')
    
    if output:
        with open(output,'w') as f:
            f.write(trees)

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
