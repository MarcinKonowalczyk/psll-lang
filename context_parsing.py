
from more_itertools import windowed
from itertools import chain

def context_split(string, delimiter=',', group='()', escape_char='\\'):
    ''' Split string at delimiter, except for in the middle of the specified context '''

    group = group+group if len(group)==1 else group
    state, last_break, escape, parts = 0, 0, False, []

    for si,char in enumerate(string):
        if escape:
            escape = False
            continue

        if state:
            # First try to match the closing group if state is already high
            # This makes matching the same delimiter for opening and closing work
            if char is group[1]: state -= 1
            elif char is group[0]: state += 1
        else:
            if char is group[0]: state += 1
            elif char is group[1]: state -= 1

        escape = char is escape_char # Escape the next char

        if char is delimiter and not state:
            parts.append(string[last_break:si])
            last_break = si+1

    parts.append(string[last_break:]) # Append last part
    return tuple(parts)


if __name__ == "__main__":
    # Will have to escape ps commands: [, ], " and \ in psll strings
    # a = '  "hello" , \\" , "\\"\\\\", arg a 7, [1,2,"s\[u\[p",[4,5,5], arg a 1], 3, [], 1, \], \], \\", 2, 3, \[, "h,,,,s,p" '

    a = '(set nil (arg 999)) ( set nargin 0) (do cond ((set nargin (+ nargin 1)) (set cond (! (= (arg nargin) nil))))) (set nargin (- nargin 1)) (out "\\(\\(nargi\\n: " nargin) (set nil (arg 999)) (set nargin 0) (do cond ((set nargin (+ nargin 1)) (set cond (! (= (arg nargin) nil))))) (set nargin (- nargin 1)) (out "\\(\\(nargin: " nargin)'
    isbracketed = lambda x: x[0]=='(' and x[-1]==')'
    for j, part in enumerate( context_split(a,delimiter=' ',group='()') ):
        # if isbracketed(part):
        print(j, part.replace(' ','_'))