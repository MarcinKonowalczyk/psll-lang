from itertools import zip_longest, tee
from itertools import product
# from math import ceil,sqrt

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class Pyramid:
    ''' Single pyramid '''

    @staticmethod
    def text2pyramid(text,min_len=0,space='.',remove_spaces=True):
        '''Put text inside of a pyramid'''
        # N = ceil(sqrt(len(text))) # Number of pyramid levels
        if remove_spaces: text = text.replace(' ','')

        # Ensure nice formatting of short keywords (without excessive space)
        if len(text)==2: text = space + text
        elif len(text)==3: text = space + text
        elif len(text)==5: text = 4*space + text
        elif len(text)==6: text = space + text[:3] + space + text[3:]
        elif len(text)==7: text = text[:4] + space + text[4:]
        elif len(text)==10: text = 4*space + text[:5] + space + text[5:]

        level = 0; lines = ['^']
        while text:
            level += 1
            i = 2*level-1
            front, text = (text[:i],text[i:])
            pad = i-len(front)
            lines.append('/' + front + pad*space + '\\')
        lines.append('-'*(2*level+1))
        grid = [(level-j+1,line,level-j+1) for j,line in enumerate(lines)]
        grid[-1] = (1,grid[-1][1],1) # Correct the padding of the final row
        return grid

    @staticmethod
    def grid2string(grid,space='.'):
        return '\n'.join([space*l + row + space*r for l,row,r in grid])

    @staticmethod
    def string2grid(string,space='.'):
        grid = []
        for row in string.split('\n'):
            i1,i2 = (0,len(row)+1)
            for i,(l1,l2) in enumerate(pairwise(row)):
                if l1==space and l2!=space and not i1: i1 = i+1
                if l1!=space and l2==space: i2 = i+1
            grid.append((i1,row[i1:i2],len(row)-i2))
        return grid

    def __init__(self,grid,space='.'):
        ''' Initialise from a grid '''
        self.height = len(grid)
        rowlen = lambda r: r[0] + len(r[1]) + r[2]
        self.width = rowlen(grid[0])
        
        for row in grid: # Sanity check on rows of the grid
            assert isinstance(row,tuple), 'All rows of the grid must be tuples'
            assert len(row)==3, 'All rows must be 3-length tuples'
            assert rowlen(row)==self.width, 'All rows must specify entries of the same length'
        
        self.grid = grid
        self.space = space
        
    @classmethod
    def from_text(self,text,space='.',**kwargs):
        ''' Initialise single-pyramid three from text '''
        grid = self.text2pyramid(text,space=space,**kwargs)
        return self(grid,space=space)

    def __repr__(self):
        grid_string = self.grid2string(self.grid,space=self.space)
        return f'<Pyramid #{hash(self)}:\n{grid_string}\n>'


class Tree(Pyramid):
    ''' Tree of pyramids '''

    def __repr__(self):
        grid_string = self.grid2string(self.grid,space=self.space)
        return f'<Tree #{hash(self)}:\n{grid_string}\n>'

    @staticmethod
    def distance_row_iterator(left,right):
        ''' Return distance of closest approach of each pair of rows '''
        for l,r in zip(left,right):
            # TODO: Add more detailed checking (making sure pyramids don't interfere)
            yield l[2]+r[0]-1

    def add_side_by_side(self,other,tight=True,min_width=None):
        ''' Add trees side-by-side '''
        s = self.space

        # Find tightest squeeze between the pyramids
        squeeze = 0
        if tight:
            squeeze = min(self.distance_row_iterator(self.grid,other.grid))
        
        # Decrease the squeeze if required by the min_width
        if min_width:
            r,l = self.grid[0],other.grid[0]
            closest_width = r[2]+l[0]-squeeze
            squeeze -= max(min_width-closest_width,0)

        squeezed_width = self.width+other.width-squeeze # Width of the squeezed pyramid
        overhang = max(self.width,other.width)-squeezed_width # Signed overhang of one pyramid over the other
        lp,rp = (max(overhang,0),0)
        if self.height>other.height: lp,rp = rp,lp

        grid = []
        for l,r in zip_longest(self.grid,other.grid):
            if l and r:
                left_pad = lp + l[0]
                middle = l[1] + (l[2]+r[0]-squeeze)*s + r[1]
                right_pad = r[2] + rp
            elif l:
                left_pad = l[0]
                middle = l[1]
                right_pad = l[2] + max(-overhang,0)
            elif r:
                left_pad = max(-overhang,0) + r[0]
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

    def add_one_child(self,other,left=True):
        ''' Add other to the tree as a left or right child '''

        # Figure out the padding and overhang spacing
        p,c = (self.grid[-1], other.grid[0])
        parent_pad = c[0]
        overhang = c[2]-(len(p[1])+p[2])

        grid = []
        for p,c in self.child_row_iterator(self.grid,other.grid):
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

    def __add__(self,other):
        istree = lambda x: isinstance(x,Tree)
        if istree(other):
            return self.add_side_by_side(other)
        elif isinstance(other,tuple) and len(other)==2:
            l,r = other
            if l and r:
                raise NotImplementedError('"Tree.add_children()" not yet implemented')
            elif l:
                return self.add_one_child(l,left=True)
                # raise NotImplementedError('"Tree.add_left_child()" not yet implemented')
            elif r:
                return self.add_one_child(r,left=False)
                # raise NotImplementedError('"Tree.add_right_child()" not yet implemented')


if __name__ == '__main__':
    # p1 = Tree.from_keyword('Quick brown fox jumped over a lazy god'*10)
    # p1 = Tree.from_keyword('Quick brown fox jumped over a lazy god')
    p1 = Tree.from_text('hello')
    p2 = Tree.from_text('Greetings traveller! Where goes thee this fine morning?'*3,remove_spaces=False)
    # p2 = Tree.from_text('Greetings traveller! Where goes thee this fine morning?')
    # p2 = Tree.from_keyword('hello')
    # print(p1 + p2 + p1 + p1 + p1 + p2)

    for j,k in product((p1,p2),repeat=2):
        print(j + (k,None))
        print(j + (None,k))

    # print(Tree(''))
    # print(Tree('1'))
    # print(Tree('12'))
    # print(Tree('set'))
    # print(Tree('seto'))
    # print(Tree('hello'))
    # print(Tree('hellos'))
    # print(Tree('1234567'))
    # print(Tree.text2pyramid('12345678'))
    # print(Tree.text2pyramid('123456789'))
    # print(Tree.text2pyramid('0123456789'))
    # print(Tree.text2pyramid('Are you Arron Burr, Sir?'))