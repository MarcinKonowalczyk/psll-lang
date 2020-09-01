from itertools import zip_longest, tee, product, islice
from abc import ABC, abstractmethod

def pairwise(iterable):
    ''' s -> (s0,s1), (s1,s2), (s2, s3), ... '''
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

#========================================================================================================================================
#                                                                                                                                        
#    ###    #####    ####  ######  #####      ###     ####  ######        ######  #####    #####  #####                                
#   ## ##   ##  ##  ##       ##    ##  ##    ## ##   ##       ##            ##    ##  ##   ##     ##                                   
#  ##   ##  #####    ###     ##    #####    ##   ##  ##       ##            ##    #####    #####  #####                                
#  #######  ##  ##     ##    ##    ##  ##   #######  ##       ##            ##    ##  ##   ##     ##                                   
#  ##   ##  #####   ####     ##    ##   ##  ##   ##   ####    ##            ##    ##   ##  #####  #####                                
#                                                                                                                                        
#========================================================================================================================================

TOP    = '^'
BOTTOM = '-'
L_SIDE = '/'
R_SIDE = '\\'
SPACE  = ' '

class AbstractTree(ABC):
    ''' Abstract Tree class '''

    @staticmethod
    def text2pyramid(text,min_width=None,remove_spaces=False):
        ''' Put text inside of a pyramid '''
        # N = ceil(sqrt(len(text))) # Number of pyramid levels
        if remove_spaces: text = text.replace(SPACE,'')
        if min_width:
            # Pad the string out such that the pyramid ends up having a correct width
            min_width = min_width//2*2+1 # Make sure width is odd
            text_pad = min_width-len(text)-2 # Figure out by how much would the text have to be padded in a single line
            text_width = ((min_width-1)//2)**2 # Desired text width
            if text_pad > 0:
                text = (text_pad//2)*SPACE + text + (text_pad-(text_pad//2))*SPACE
            text = (text_width-len(text))*SPACE + text # Pad out the rest

        # Ensure nice formatting of short keywords (without excessive SPACE)
        if len(text)==2: text = SPACE + text
        elif len(text)==3: text = SPACE + text
        elif len(text)==5: text = 4*SPACE + text
        elif len(text)==6: text = SPACE + text[:3] + SPACE + text[3:]
        elif len(text)==7: text = text[:4] + SPACE + text[4:]
        elif len(text)==10: text = 4*SPACE + text[:5] + SPACE + text[5:]

        level = 0; lines = [TOP,]
        while text:
            level += 1
            i = 2*level-1
            front, text = (text[:i],text[i:])
            pad = i-len(front)
            lines.append(L_SIDE + front + pad*SPACE + R_SIDE)
        lines.append(BOTTOM*(2*level+1))
        grid = [(level-j+1,line,level-j+1) for j,line in enumerate(lines)]
        grid[-1] = (1,grid[-1][1],1) # Correct the padding of the final row
        return grid

    @staticmethod
    def grid2string(grid):
        return '\n'.join([SPACE*l + row + SPACE*r for l,row,r in grid])

    @staticmethod
    def string2grid(string):
        grid = []
        for row in string.split('\n'):
            i1, i2 = 0, len(row)
            for i,(l1,l2) in enumerate(pairwise(row)):
                if l1==SPACE and l2!=SPACE and not i1: i1 = i+1
                if l1!=SPACE and l2==SPACE: i2 = i+1
            grid.append((i1,row[i1:i2],len(row)-i2))
        return grid

    def __init__(self,grid):
        ''' Initialise from a grid '''
        self.height = len(grid)
        rowlen = lambda r: r[0] + len(r[1]) + r[2]
        self.width = rowlen(grid[0])
        
        for row in grid: # Sanity check on rows of the grid
            assert isinstance(row,tuple), 'All rows of the grid must be tuples'
            assert len(row)==3, 'All rows must be 3-length tuples'
            assert rowlen(row)==self.width, 'All rows must specify entries of the same length'

        self.grid = grid
        
    @classmethod
    def from_text(cls,text,**kwargs):
        ''' Initialise from keyword text '''
        grid = cls.text2pyramid(text,**kwargs)
        return cls(grid)
    
    @classmethod
    def from_str(cls,string):
        ''' Initialise from string representation '''
        grid = cls.string2grid(string)
        return cls(grid)
        
    @abstractmethod
    def toTree(self):
        return
    
    @abstractmethod
    def toPyramid(self):
        return

    def __str__(self):
        return self.grid2string(self.grid)

    def __repr__(self):
        return f'<{type(self).__name__} #{hash(self)}:\n{str(self)}\n>'

    def __getitem__(self,key):
        return self.grid[key]

    def __setitem__(self,key,value):
        self.grid[key] = value

    def __hash__(self):
        return hash(tuple(self.grid)) # Trees hash the same if their grids are the same

#==============================================================================================
#                                                                                              
#  #####   ##    ##  #####      ###    ###    ###  ##  ####                                  
#  ##  ##   ##  ##   ##  ##    ## ##   ## #  # ##  ##  ##  ##                                
#  #####     ####    #####    ##   ##  ##  ##  ##  ##  ##  ##                                
#  ##         ##     ##  ##   #######  ##      ##  ##  ##  ##                                
#  ##         ##     ##   ##  ##   ##  ##      ##  ##  ####                                  
#                                                                                              
#==============================================================================================

class Pyramid(AbstractTree):
    ''' Single pyramid '''

    def __init__(self,grid):
        super().__init__(grid)
        assert self[0][1] == TOP, 'Pyramid has an invalid top'
        for row,next_row in pairwise(self):
            assert row[0]==row[2], 'Not a pyramid'
            if not (row[0]==1 and next_row[0]==1):
                assert (row[0]-1)==next_row[0], 'Not a pyramid'

    @property
    def content(self):
        content = ''.join(row[1:-1].replace(SPACE,'')
            for _,row,_ in islice(self,1,self.height-1))
        return content.strip()

    def toTree(self):
        return Tree(self.grid)

    def toPyramid(self):
        return self

    def __add__(self,other):
        ''' Overload the + operator by passing self to Tree '''
        if isinstance(other,AbstractTree):
            return self.toTree() + other.toTree()
        elif isinstance(other,tuple) and len(other)==2:
            return self.toTree() + other
        else:
            raise TypeError(f"unsupported operand type for +: '{type(self).__name__}' and '{type(other).__name__}'")

#=================================================================
#                                                                 
#  ######  #####    #####  #####                                
#    ##    ##  ##   ##     ##                                   
#    ##    #####    #####  #####                                
#    ##    ##  ##   ##     ##                                   
#    ##    ##   ##  #####  #####                                
#                                                                 
#=================================================================

class Tree(AbstractTree):
    ''' Tree of pyramids '''

    @staticmethod
    def distance_row_iterator(left,right):
        ''' Return distance of closest approach of each pair of rows '''
        for l,r in zip(left,right):
            distance = l[2]+r[0]
            lc, rc = l[1][-1], r[1][0]
            if (lc==TOP and rc == BOTTOM) or (lc==BOTTOM and rc == TOP):
                distance -= 1
            yield distance

    def add_side_by_side(self,other,tight=True,min_spacing=None,odd_spacing=False):
        ''' Add trees side-by-side '''
        # Find tightest squeeze between the pyramids
        squeeze = 0
        if tight:
            squeeze = min(self.distance_row_iterator(self,other))
        
        # Decrease the squeeze if required by the min_width
        l,r = self[0],other[0]
        p2p_distance = l[2]+r[0]-squeeze
        if min_spacing:
            squeeze -= max(min_spacing-p2p_distance,0)
            p2p_distance = l[2]+r[0]-squeeze

        # Width of the squeezed pyramid
        squeezed_width = self.width + other.width - squeeze

        # Make sure spacing between the peaks is an odd
        if odd_spacing and not (p2p_distance%2):
            squeeze -= 1
            squeezed_width +=1

        # Figure out signed overhang of one tree over the other and therefore the top padding
        if self.height>other.height:
            overhang = other.width-squeeze
            lp, rp = 0, max(-overhang,0)
        else:
            overhang = self.width-squeeze
            lp, rp = max(-overhang,0), 0

        # Put together self and the other row by row
        grid = []
        for l,r in zip_longest(self,other):
            if l and r:
                left_pad = lp + l[0]
                middle = l[1] + (l[2]+r[0]-squeeze)*SPACE + r[1]
                right_pad = r[2] + rp
            elif l:
                left_pad = l[0]
                middle = l[1]
                right_pad = l[2] + max(overhang,0)
            elif r:
                left_pad = max(overhang,0) + r[0]
                middle = r[1]
                right_pad = r[2]
            row = (left_pad,middle,right_pad)
            grid.append(row)

        return Tree(grid)

    @staticmethod
    def child_row_iterator(parent,child):
        ''' Yield rows from parent and then from the child, signalling the changeover '''
        parent,child = iter(parent), iter(child)
        for row,next_row in pairwise(parent):
            if next_row is not None:
                yield (row, None)
        yield (next_row, next(child)) # Intermediate row
        for row in child:
            yield (None, row)

    def add_one_child(self,child,left=True):
        ''' Add a left or right child to the tree '''
        assert isinstance(child,AbstractTree), 'The child must be a Tree or a Pyramid'
        # child = child.toTree() # The child doesn't actually need to be a tree

        # Figure out the padding and overhang spacing
        p, c = self[-1], child[0] # Last row of parent and first of the child
        parent_pad = c[0] if left else c[2]
        overhang = c[2]-(len(p[1])+p[2]) if left else c[0]-(len(p[1])+p[2])
        
        grid = []
        for p,c in self.child_row_iterator(self,child):
            if p and not c:
                left_pad = parent_pad + p[0] if left else max(overhang,0) + p[0]
                middle = p[1]
                right_pad = p[2] + max(overhang,0) if left else p[2] + parent_pad
            elif p and c:
                left_pad = c[0] if left else max(overhang,0) + p[0]
                middle = c[1] + p[1] if left else p[1] + c[1]
                right_pad = p[2] + max(overhang,0) if left else c[2]
            elif not p and c:
                left_pad = c[0] if left else max(-overhang,0) + c[0]
                middle = c[1]
                right_pad = c[2] + max(-overhang,0) if left else c[2]
            row = (left_pad,middle,right_pad)
            grid.append(row)
        return Tree(grid)

    def add_two_children(self,left,right):
        ''' Add left and right child to a tree '''

        try: # Parent *must* be a single pyramid, even if children would fit
            parent = self.toPyramid()
        except:
            raise RuntimeError('Cannot expand non-singleton Trees')

        parent_width = len(self[-1][1])//2*2+1 # Make sure parent width is odd

        # Put children together with minimum width of a parent, make sure they're odd
        left, right = left.toTree(), right.toTree()
        children = left.add_side_by_side(right,min_spacing=parent_width,odd_spacing=True)
        actual_children_width = len(children[0][1])-2

        # Try to expand oneself to accommodate the width of the children
        if (actual_children_width > parent_width) or (parent_width>len(self[-1][1])):
            parent = Tree.from_text(parent.content,min_width=actual_children_width)
        else:
            parent = self

        parent_left_pad, _, parent_right_pad = children[0]

        grid = []
        for p,c in self.child_row_iterator(parent,children):
            if p and not c:
                left_pad = parent_left_pad + p[0]
                middle = p[1]
                right_pad = p[2] + parent_right_pad
            elif p and c:
                left_pad = c[0]
                middle = c[1][0] + p[1] + c[1][-1]
                right_pad = c[2]
            elif not p and c:
                left_pad, middle, right_pad = c
            row = (left_pad,middle,right_pad)
            grid.append(row)
        
        return Tree(grid)

    def toTree(self):
        return self

    def toPyramid(self):
        return Pyramid(self.grid)

    def __add__(self,other):
        if isinstance(other,AbstractTree):
            return self.add_side_by_side(other.toTree())
        elif isinstance(other,tuple) and len(other)==2:
            l,r = other
            if l and r:
                return self.add_two_children(l,r)
                # raise NotImplementedError('"Tree.add_children()" not yet implemented')
            elif l:
                return self.add_one_child(l,left=True)
                # raise NotImplementedError('"Tree.add_left_child()" not yet implemented')
            elif r:
                return self.add_one_child(r,left=False)
                # raise NotImplementedError('"Tree.add_right_child()" not yet implemented')
            else: # self + (None,None)
                return self
        else:
            raise TypeError(f"unsupported operand type for +: '{type(self).__name__}' and '{type(other).__name__}'")


#======================================================================
#                                                                      
#  ###    ###    ###    ##  ##     ##                                
#  ## #  # ##   ## ##   ##  ####   ##                                
#  ##  ##  ##  ##   ##  ##  ##  ## ##                                
#  ##      ##  #######  ##  ##    ###                                
#  ##      ##  ##   ##  ##  ##     ##                                
#                                                                      
#======================================================================

if __name__ == '__main__':
    p0 = Pyramid.from_text('')
    p1 = Pyramid.from_text('set')
    text = 'Greetings traveller! Where goes thee this fine morning?'*3
    p2 = Pyramid.from_text(text,remove_spaces=False)
    p3 = (p1+p1+p1)+p2
    
    for i,j,k in product((p0,p1,p2),repeat=3):
        print()
        print(i + (j,k))