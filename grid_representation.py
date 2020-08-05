from itertools import zip_longest

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
        pyramid += ' /' + text + '\\ \n'
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
        padded_grid = []
        for i,row in enumerate(grid):
            pad = '.'*(len(grid)-i-1)
            padded_grid.append(pad + row + pad)
        return '\n'.join(padded_grid)

    @staticmethod
    def string2grid(string):
        string = string.split('\n')
        middle = (len(string[0])-1)//2
        return [row[(middle-i):(middle+i+1)] for i,row in enumerate(string)]

    def __init__(self,grid):
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
    def width(self):
        return len(self.grid[-1])
    
    @property
    def height(self):
        return len(self.grid)
    @property
    def middle(self):
        return (self.width-1)//2

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

    def add_pyramid(self,other,min_width=0):
        # squeeze = 1
        new_grid = []
        s = self.space
        for i,(l,r) in enumerate(zip_longest(self.grid,other.grid,fillvalue='')):
            if l and r:
                left_pad = max(self.middle-i,other.middle-i-self.width)*s
                middle_pad = s*(2*min(self.middle,other.middle)-2*i)
                right_pad = max(self.middle-i-other.width,other.middle-i)*s
            elif l:
                left_pad = (self.middle-i)*s
                middle_pad = ''
                right_pad = max(self.middle-i,other.width-i+other.height-1)*s
            elif r:
                left_pad = max(other.middle-i,self.width-i+self.height-1)*s
                middle_pad = ''
                right_pad = (other.middle-i)*s
            print(left_pad + l + middle_pad + r + right_pad)
        print()
        return Pyramid(new_grid)

if __name__ == '__main__':
    # p1 = Pyramid.from_keyword('Quick brown fox jumped over a lazy dog')
    p1 = Pyramid.from_keyword('Quick brown fox jumped')
    # p1 = Pyramid.from_keyword('hello')
    # p2 = Pyramid.from_keyword('Greetings traveller! Where goes thee this fine morning?')
    # p2 = Pyramid.from_keyword('Greetings traveller!')
    p2 = Pyramid.from_keyword('hello')
    p1.add_pyramid(p2)
    # print(p1.middle,p1.grid[0][p1.middle])