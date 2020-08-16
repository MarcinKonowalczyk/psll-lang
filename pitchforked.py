# PR #455 from more_itertools

from collections import deque

def pitchforked(seq, n=1):
    """Splits the iterable into three pieces, with the middle piece of width *n* (the width of the pitchfork). Returns the prefix, middle and the suffix. Similar to :func:`windowed`, but allows reconstruction of the full sequence from each split.

    >>> for p in pitchforked('ABCDEF', 2):
    ...     print(*map(lambda x: ''.join(x),p))
     AB CDEF
    A BC DEF
    AB CD EF
    ABC DE F
    ABCD EF 

    To obtain every partitioning of a sequence, use :func:`chain` and :func:`map` to iterate over all possible partitioning lengths in one go:

    >>> from itertools import chain
    >>> from functools import partial
    >>> every_pitchfork = lambda seq: chain(*map(
    ...     partial(pitchforked,seq),range(len(seq))))
    >>> sequence = 'ABCDE'
    >>> for p in every_pitchfork(sequence):
    ...     print(*map(lambda x: ''.join(x),p))
      ABCDE
    A  BCDE
    AB  CDE
    ABC  DE
    ABCD  E
    ABCDE  
     A BCDE
    A B CDE
    AB C DE
    ABC D E
    ABCD E 
     AB CDE
    A BC DE
    AB CD E
    ABC DE 
     ABC DE
    A BCD E
    AB CDE 
     ABCD E
    A BCDE 

    A nested lambda function can also be used instead of :func:`partial`:

    >>> from itertools import chain
    >>> every_pitchfork = lambda seq: chain(*map(
    ...     lambda n: pitchforked(seq,n),range(len(seq))))
    """
    if n < 0:
        raise ValueError('n must be >= 0')
    if n > len(seq):
        raise ValueError('n must be <= len(seq)')
    
    prefix, hay, suffix = deque(), deque(), deque(seq)
    for _ in range(n):
        hay.append(suffix.popleft())
    yield tuple(prefix), tuple(hay), tuple(suffix)

    for _ in range(len(suffix)):
        hay.append(suffix.popleft())
        prefix.append(hay.popleft())
        yield tuple(prefix), tuple(hay), tuple(suffix)

if __name__=="__main__":

    from itertools import chain
    from functools import partial
    
    sequence = 'ABCDE'

    every_partition = lambda seq: chain(*map(
        partial(pitchforked,seq),range(len(seq))))
    for partitions in every_partition(sequence):
        print(*map(lambda x: ''.join(x),partitions))
