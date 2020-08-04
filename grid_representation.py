from ll2pyra import text_to_pyramid

class Grid:
    '''
    Grid of symbols
    '''

    def __init__(self,text):
        # Check symbols is a list of lists
        self.grid = [[letter for letter in row] for row in text.split('\n')]


    def __repr__(self):
        return '\n'.join([''.join(row) for row in self.grid])

if __name__ == '__main__':
    g = Grid(text_to_pyramid('hi'))
    print(g)