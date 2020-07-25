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
    pyramid += space + '-'*(2*level+1) + space
    
    return pyramid

def build_tree_bottom_up(tree,space='.'):
    if len(tree)==1:
        return text_to_pyramid(tree[0])
    elif len(tree)==2:
        root = text_to_pyramid(tree[0]).split('\n')
        left_leaf = text_to_pyramid(tree[1]).split('\n')
        
        # Find apex of left leaf
        root_pad = left_leaf[0].find('^')

        # Stitch together
        root = [space*root_pad + row for row in root]
        root[-1] = re.sub(f'{re.escape(space)}(?=-+)','^',root[-1])
        tree = root + left_leaf[1:]
        tree_width = max(len(l) for l in tree)
        tree = [line + (tree_width-len(line))*space for line in tree]

        tree = '\n'.join(tree)

    elif len(tree)==3:
        left_leaf = text_to_pyramid(tree[1]).split('\n')
        right_leaf = text_to_pyramid(tree[2]).split('\n')

        # Put children together
        fillvalue = space*len(left_leaf[0]) if len(left_leaf)<len(right_leaf) else space*len(right_leaf[0])
        children = [l+r for l,r in zip_longest(left_leaf,right_leaf,fillvalue=fillvalue)]

        left_peak = children[0].find('^')
        right_peak = children[0].rfind('^')
        min_len = right_peak-left_peak-2
        root = text_to_pyramid(tree[0],min_len=min_len).split('\n')

        root = [space*left_peak + row for row in root]
        root[-1] = re.sub(f'{re.escape(space)}(-+){re.escape(space)}',r'^\1^',root[-1])
        tree = root + children[1:]
        tree_width = max(len(l) for l in tree)
        tree = [line + (tree_width-len(line))*space for line in tree]
        for line in tree:
            print(line)

    else:
        raise SyntaxError('Invalid number of input arguments')

    return tree

if __name__ == "__main__":
    text = readfile('test_1.ll')
    # print(text)
    lines = split_into_trees(text)
    # print(lines)
    tree = split_into_subtrees(lines[2])
    # print(tree)
    # pyramid = text_to_pyramid('AB')
    p = build_tree_bottom_up(['asda','hello','123'])
    print(p)
