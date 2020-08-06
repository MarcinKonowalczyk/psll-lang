from itertools import zip_longest

from itertools import tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

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
        pyramid = space*(level+2) + '^' + space*(level+2) + '\n'
        for j in range(level):
            pyramid += space*(level-j+1) + '/' + space*(j*2+1) + '\\' + space*(level-j+1) + '\n'
        pyramid += space + '/' + text + '\\' + space + '\n'
        pyramid += space*1 + '-'*(2*level+3) + space*1
    
    else:
        pyramid = ' ^ \n - ' # Null pyramid
    
    return pyramid

class Pyramid:
    '''
    Pyramid or tree of pyramids
    '''

    @staticmethod
    def grid2string(grid):
        s = '.'
        return '\n'.join([s*l+row+s*r for l,row,r in grid])

    @staticmethod
    def string2grid(string):
        s = '.'
        grid = []
        for row in string.split('\n'):
            i1,i2 = (0,len(row)+1)
            for i,(l1,l2) in enumerate(pairwise(row)):
                if l1==s and l2!=s and not i1: i1 = i+1
                if l1!=s and l2==s: i2 = i+1
            grid.append((i1,row[i1:i2],len(row)-i2))
        return grid
        # middle = (len(string[0])-1)//2
        # return [row[(middle-i):(middle+i+1)] for i,row in enumerate(string)]

    def __init__(self,grid):
        
        self.height = len(grid)
        
        rowlen = lambda r: r[0] + len(r[1]) + r[2]
        self.width = rowlen(grid[0])
        for row in grid:
            assert isinstance(row,tuple), 'All rows of the grid must be tuples'
            assert len(row)==3, 'All rows must be 3-length tuples'
            assert rowlen(row)==self.width, 'All rows must specify entries of the same length'
        
        self.space = '.'
        self.grid = grid
    
    @classmethod
    def from_string(self,string):
        return Pyramid(self.string2grid(string))

    @classmethod
    def from_keyword(self,keyword):
        string = text_to_pyramid(keyword)
        return Pyramid.from_string(string)

    def __repr__(self):
        return f'<Grid #{hash(self)}:\n' + self.grid2string(self.grid) + '\n>'

    @property
    def empty_row(self):
        return self.space*len(self.grid[-1])
    def infinite_rows(self):
        for row in self.grid:
            yield row
        # Thereafter keep yielding empty space of the correct size
        N = len(row)
        while True:
            N += 2
            yield N*self.space

    @staticmethod
    def row_iterator(left,right):
        for l,r in zip(left,right):
            # TODO: Add more detailed checking (making sure pyramids don't interfere)
            yield l[2]+r[0]-1

    def add_pyramid(self,other,tight=True,min_width=None):
        new_grid = []
        s = self.space

        # Find tightest squeeze between the pyramids
        squeeze = 0
        if tight:
            squeeze = min(self.row_iterator(self.grid,other.grid))
        
        # Decrease the squeeze if required by the min_width
        if min_width:
            r,l = self.grid[0],other.grid[0]
            closest_width = r[2]+l[0]-squeeze
            squeeze -= max(min_width-closest_width,0)

        squeezed_width = self.width+other.width-squeeze # Width of the squeezed pyramid
        # width = max(squeezed_width,self.width,other.width) # Actual width of the pyramid
        overhang = max(self.width,other.width)-squeezed_width # Signed overhang of one pyramid over the other
        lp,rp = (max(overhang,0),0)
        if self.height>other.height: lp,rp = rp,lp

        new_grid = []
        for l,r in zip_longest(self.grid,other.grid):
            if l and r:
                left_pad = lp + l[0]
                middle = l[1] + (l[2]+r[0]-squeeze)*s + r[1]
                right_pad = r[2] + rp
            elif l:
                left_pad = l[0]
                middle = l[1]
                right_pad = l[2]+max(0,-overhang)
            elif r:
                left_pad = max(0,-overhang)+r[0]
                middle = r[1]
                right_pad = r[2]
            row = (left_pad,middle,right_pad)
            print(row[0]*s + row[1] + row[2]*s)
            new_grid.append(row)
        return Pyramid(new_grid)

if __name__ == '__main__':
    # p1 = Pyramid.from_keyword('Quick brown fox jumped over a lazy dog')
    p1 = Pyramid.from_keyword('Quick brown fox jumped')
    # p1 = Pyramid.from_keyword('hello')
    # p2 = Pyramid.from_keyword('Greetings traveller! Where goes thee this fine morning?')
    # p2 = Pyramid.from_keyword('Greetings traveller!')
    p2 = Pyramid.from_keyword('hello')
    # print(p1.add_pyramid(p2))
    p3 = p1.add_pyramid(p2)
    # print(p3.add_pyramid(p1).add_pyramid(p1))
    # print(p1.middle,p1.grid[0][p1.middle])