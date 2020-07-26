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
        (r'((?<=\()\s+|\s+(?=\)))','')) # Spaces inside brackets

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
    text = text.replace(' ','')
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
    
    return pyramid

def build_tree_bottom_up(tree,space='.'):
    
    assert isinstance(tree,list), f'Tree must be a list ({tree})'
    if not isinstance(tree[0],str):
        tree = [''] + tree

    if len(tree)==1:
        if isinstance(tree[0],str):
            return text_to_pyramid(tree[0],space=space)
        else:
            return build_tree_bottom_up(tree[0],space=space)
    elif len(tree)==2:
        root = text_to_pyramid(tree[0],space=space).split('\n')
        if isinstance(tree[1],str):
            left_leaf = text_to_pyramid(tree[1],space=space)
        else:
            left_leaf = build_tree_bottom_up(tree[1],space=space)
        left_leaf = left_leaf.split('\n')

        # Find apex of left leaf
        root_pad = left_leaf[0].find('^')+1

        # Stitch together
        root = [space*root_pad + row for row in root]
        root[-1] = re.sub(f'{re.escape(space)}(?=-+)','^',root[-1])
        tree = root + left_leaf[1:]
        tree_width = max(len(l) for l in tree)
        tree = [line + (tree_width-len(line))*space for line in tree]

        tree = '\n'.join(tree)

    elif len(tree)==3:
        if isinstance(tree[1],str):
            left_leaf = text_to_pyramid(tree[1],space=space)
        else:
            left_leaf = build_tree_bottom_up(tree[1],space=space)
        left_leaf = left_leaf.split('\n')
        
        if isinstance(tree[2],str):
            right_leaf = text_to_pyramid(tree[2],space=space)
        else:
            right_leaf = build_tree_bottom_up(tree[2],space=space)
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

def compile(text,space=' '):
    '''
    Compile text into trees
    '''
    trees = split_into_trees(text)
    trees = [split_into_subtrees(tree) for tree in trees]
    trees = [build_tree_bottom_up(tree,space=space) for tree in trees]
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

# if __name__ == "__main__":
#     text = readfile('golf.ll')
#     trees = compile(text)
#     print(trees)
#     trees = compact(trees)
#     print(trees)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==1:
        print('Compiles lisp-like syntax to Pyramid Scheme')
        print('ll2ps <input filename> <output filename>')
    elif len(sys.argv)==3:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
        print('Input filename:',input_filename)
        print('Output filename:',output_filename)
        
        text = readfile(input_filename)
        
        print('Reduced source:')
        print(text)
        
        trees = compile(text)
        trees = compact(trees)

        print('Pyramid scheme:')
        print(trees)

        with open(output_filename,'w') as f:
            f.write(trees)
    else:
        raise SyntaxError('Invalid number of input arguments')
    