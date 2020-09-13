import re

SPACE = ' '
COMMA = ','
def f(string):
    string = string[1:-1].strip()
    if not string:
        return ('-',('0','0'),('0','0')) # Make an empty array

    last_start = 0
    last_quote = '' # Keep track of quotation marks
    delimiter = '' # Don't know the delimiter yet
    tokens = []
    for j,char in enumerate(string):

        # Enter and exit psll strings
        for quote in ['"','\'']:
            if char==quote:
                if not last_quote: last_quote = quote # Start a quote
                elif last_quote==quote: last_quote = '' # End a quote
        
        if not delimiter: # Figure out the delimiter on the first go
            if not last_quote:
                if char == SPACE:
                    delimiter = SPACE
                    print('space delimiter found')
                elif char == COMMA:
                    delimiter = COMMA
                    print('comma delimiter found')
        else:
            pass

        part = string[last_start:j+1]
        last_start = j+1
        # print('part:', part.replace(' ','_'))

        tokens.append(part)
    print('tokens:',tokens)

if __name__=="__main__":

    # strings = ("[]","[ ]","[   ]")
    #strings = ("[1]","[ 1]","[1 ]")
    strings = ("[1 ,2]",)#,"[1,2,3]","[1, 2]","[1,2 ,3]")

    for s in strings:
        print(s, f(s))