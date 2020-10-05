
from more_itertools import windowed
from itertools import chain

def group_split(string, delimiter=',', groups=None, escape_char='\\'):
    ''' Split string at delimiter, except for in the middle of the specified groups '''

    groups = tuple(map(lambda x: x if len(x)==2 else x+x,groups)) if groups else ()
    state = [0 for _ in groups] # States of each of the group

    escape = False
    last_break = 0
    parts = []

    for si,char in enumerate(string):

        if escape:
            escape = False
            continue

        for gi,g in enumerate(groups):
            other_state = [s for i,s in enumerate(state) if i is not gi]
            # if not any(other_state):
            if state[gi]:
                # First try to match the closing group if state is already high
                # This make matching the same delimiter for opening and closing work
                if char is g[1]: state[gi] -= 1
                elif char is g[0]: state[gi] += 1
            else:
                if char is g[0]: state[gi] += 1
                elif char is g[1]: state[gi] -= 1

        escape = char is escape_char # Escape the next char

        if char is delimiter and not any(state):
            parts.append(string[last_break:(si)])
            last_break = si+1

        print(char, state)
    parts.append(string[last_break:])
    return tuple(parts)


if __name__ == "__main__":
    # Will have to escape ps commands: [, ], " and \ in psll strings
    # a = '  "hello" , \\" , "\\"\\\\", arg a 7, [1,2,"s\[u\[p",[4,5,5], arg a 1], 3, [], 1, \], \], \\", 2, 3, \[, "h,,,,s,p" '

    a = '(set nil (arg 999)) (set nargin 0) (do cond ((set nargin (+ nargin 1)) (set cond (! (= (arg nargin) nil))))) (set nargin (- nargin 1)) (out "((nargin: " nargin) (set nil (arg 999)) (set nargin 0) (do cond ((set nargin (+ nargin 1)) (set cond (! (= (arg nargin) nil))))) (set nargin (- nargin 1)) (out "((nargin: " nargin)'
    # print(a)
    groups = ('()','"')
    # groups = ('[]','"')

    for j, part in enumerate( group_split(a,delimiter=' ',groups=groups) ):
        print(j, part)