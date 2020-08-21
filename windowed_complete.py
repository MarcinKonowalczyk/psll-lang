# PR #455 from more_itertools

def windowed_complete(iterable, n=1):
    """
    Yield ``(beginning, middle, end)`` tuples, where:
    * Each ``middle`` has *n* items from *iterable*
    * Each ``beginning`` has the items before the ones in ``middle``
    * Each ``end`` has the items after the ones in ``middle``

    >>> iterable = range(7)
    >>> n = 3
    >>> for beginning, middle, end in windowed_complete(iterable, n):
    ...     print(beginning, middle, end)
    () (0, 1, 2) (3, 4, 5, 6)
    (0,) (1, 2, 3) (4, 5, 6)
    (0, 1) (2, 3, 4) (5, 6)
    (0, 1, 2) (3, 4, 5) (6,)
    (0, 1, 2, 3) (4, 5, 6) ()

    *n* can have values between 0 and length of the iterable. ValueError will be raised for value of *n* outside of that range. Note that, in order to assert the ``n<len(iterable)`` case, the interable has to get consumed.

    To obtain every such partitioning of a sequence, use :func:`chain` and :func:`map` to iterate over all possible partitioning lengths in one go:

    >>> from itertools import chain
    >>> from functools import partial
    >>> every_partition = lambda seq: chain(*map(
    ...     partial(windowed_complete,seq),range(len(seq))))
    >>> sequence = 'ABC'
    >>> for p in every_partition(sequence):
    ...     print(*map(lambda x: ''.join(x),p),sep='|',end=' ')
    ||ABC A||BC AB||C ABC|| |A|BC A|B|C AB|C| |AB|C A|BC| 

    A nested lambda function can also be used instead of :func:`partial`:

    >>> from itertools import chain
    >>> every_partition = lambda seq: chain(*map(
    ...     lambda n: windowed_complete(seq,n),range(len(seq))))
    """
    if n < 0:
        raise ValueError('n must be >= 0')
    
    seq = tuple(iterable)
    size = len(seq)

    if n > size:
        raise ValueError('n must be <= len(seq)')

    for i in range(size - n + 1):
        beginning = seq[:i]
        middle = seq[i: i + n]
        end = seq[i + n:]
        yield beginning, middle, end

if __name__ == "__main__":

    from english_words import english_words_set

    for word in english_words_set:
        if len(word)>2: # No short words
            for b,m,e in windowed_complete(word,2):
                if m[0]!=m[1]: # No double letters
                    new_word = ''.join(b) + m[1] + m[0] + ''.join(e)
                    new_word = new_word.lower()
                    if new_word in english_words_set:
                        print(word,new_word)