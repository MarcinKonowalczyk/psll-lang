# psll-lang

[![Build Status](https://travis-ci.org/MarcinKonowalczyk/psll-lang.svg?branch=master)](https://travis-ci.org/MarcinKonowalczyk/psll-lang) [![Coverage Status](https://coveralls.io/repos/github/MarcinKonowalczyk/psll-lang/badge.svg?branch=master)](https://coveralls.io/github/MarcinKonowalczyk/psll-lang?branch=master)

A lisp-like language which compiles to [pyramid scheme](https://github.com/ConorOBrien-Foxx/Pyramid-Scheme) (**p**yramid **s**cheme **l**isp-**l**ike syntax, aka `psll`).

## Installation

Make  `psll.py` executable:

```
chmod u+x psll.py
```
or use the `psll.sh` bash script which you might want to edit to make it point to the correct files. It compiles and runs a program.

## Use

Read the help:
```
./psll.py -h
```

Verbose output and save to the file:
```
./psll.py ./examples/bubble_sort.psll -o -v
```

## Examples

The following is an example lisp-like pyramid scheme which counts the number of input arguments it gets, and then prints it out to the command line. The syntax supports `//` comments and newlines, as well as (almost) random additions of whitespace.

For the purposed of the markdown README, C# highlighting seems to look fine. There is a vscode extension in the `psll-lang` folder which provides syntax highlighting for both psll and Pyramid Scheme.

```c#
// Make nil by asking for the 999'th input argument
(set nil (arg 999))

// Count the number of input arguments - n
(set nargin 0)
(do cond (
    (set nargin (+ nargin 1))
    (set cond (! (= (arg nargin) nil)))
))
(set nargin (- nargin 1))

(out "nargin: " nargin) // Print
```

It can be compiled and run as follows:

```
./psll.py ./examples/nargin_counter.psll -o -f
ruby ./Pyramid-Scheme/pyra.rb ./exmaples/nargin_counter.pyra 4 3 5 2 4
```

or with the `psll.sh` bash script:

```
./psll.sh ./examples/nargin_counter.psll 4 3 5 2 4
```

The output is `nargin: 5`

## Additional features

Psll implements a few bits of syntactic sugar, to make writing complicated pyramid schemes easier.

### Bracket expansion
A bracket with multiple subtrees will get automatically split into multiple size-2 subtrees which will, in turn, get prepended with the empty string, as described above. Hence, the following psll code:

```cs
(
  (out 1) (out 2) (out 3) (out 4) (out 5)
)
```

will get interpreted as:

```cs
(
  (
    ( // First pair
      (out 1) (out 2)
    )
    ( // Second pair
      (out 3) (out 4)
    )
  ) // One left
  (out 5)
)
```

The elements are taken from the list pairwise, and put into sub-lists recursively, until the root list has length of 2 or less. Because of order of subtree evaluation in pyramid scheme, this preserves the execution order. Note that arbitrary indentation, and mid-line comments are allowed.

This feature is useful, for example, for keeping tidy the body of a for-loop or an if-statement:

```cs
(set a 0) // Flip-flop
(set N 10) (set j 0) // N of iteration and loop counter
(loop (! (= j N)) (
    // Do some work...
    (out j (chr 32)) // Print j and space
    (out a (chr 10)) // Print a and newline
    (set a (! a)) // Flip a
(set j (+ j 1))
))
```

### Strings

In pyramid scheme, the strings have to be built manually. The string hello is:

```cs
(set a (+ (+ (+ (+ (chr 72) (chr 101)) (chr 108)) (chr 108)) (chr 111)))
```

Psll expands a string literal into such construct, so its enough to write:

```cs
(set a "Hello")
```

Only `"` can be used to create strings.

### Def keyword

Psll implements `def` as a special keyword. The syntax for `def` is: `(def x (...))`, where `x` can be any string (except `def`) and `(...)` is any bracket. From that point onwards, each occurrence of `x` or `(x)` is replaced by the bracket `(...)`. The `def` statement itself gets replaced by an empty pyramid (hence evaluates to 0). For example:

```cs
(def f (set a (! a))) // This becomes ()
(f) // This becomes (set a (! a))
```

`def` can, therefore be used akin to a function definition:

```cs
(set a 0)
(def incr (set a (+ a 1))) // Increment a
(incr) // This now becomes (set a (+ a 1))
(out "a: " a) (out (chr 10))
```

Once defined, it is possible to redefine `def`'s in terms of themselves:
```cs
(def incr ( // Redefine 'incr' as itself + printing
    (incr)
    (out "<incr> a: " a)
    (out (chr 10)) // Newline
))
(incr) // This now does the original incr + print
```

Defs are active **within the scope in which they are declared**. Hence:
```cs
(def f (incr)) // 'f' is an alias for 'incr'
(f) // This now behaves as 'incr'
(
    (out "entering scope" (chr 10))
    (def f (out "Vikings approaching!" (chr 10))) // Redefine f within the scope
    (f f f) // Do 'f' 3 times
    (out "leaving scope" (chr 10))
)
(out "a: " a) (out (chr 10)) // But 'a' remains unchanged
(f) // 'f' works the same way as before the scope
(incr) // and 'incr' also works the same way
```

The code above prints `Vikings approaching!` three times, as opposed to incrementing `a` three times, btu then goes back to incrementing after the scope. 

The following is, for example, a *postfix* implementation of the modulo function:

```cs
(def mod (loop (<=> (<=> a b) -1) (set a (- a b)))) // Set a to mod(a,b)
(set a 11) (set b 7) (mod)
```

### Command expansion

The `out` command of Pyramid Scheme allows for output of, at most, 2 variables. To output more, one needs to chain mutiple such `out` statements. In psll an out command with more than two inputs gets automatically expanded into such chain, such that:

```cs
(out a b)
(out c d)
(out e)
```

can be written simply as:

```cs
(out a b c d e)
```

The former might, however be preferable in certain contexts since it allows for comments on each part of the `out`.

A _similar_ expansion will is also implemented for binary operators `+`, `*` as well as `-`, `/`, `^`, `=` and `<=>`, such that:

```cs
(+ 1 2 3 4) // This
(out (+ (+ (+ 1 2) 3) 4) newline) // Becomes this
```

Addition and subtraction are commutative over the set of all possible inputs, and hence the exact order of operations does not matter. (This is not quite true. String multiplication overloads concatenation and that's not commutative). For a non-commutative operation, e.g. subtraction, the expansion order does matter. Hence:

```cs
(- 1 2 3 4) // This
(- (- (- 1 2) 3) 4) // Does indeed expand into this
```

but,

```cs
(1 2 3 4 -) // This
(- 1 (- 2 (- 3 4))) // Expands to this instead
```

For the binary operations listed above, they can be specified at the end of the bracket to perform a right-associative expansion.

For the sake of compatibility with non-expanded brackets, the following two are also allowed, and identical:

```cs
(- 1 2)
(1 2 -)
```
(and, of course, the same for other binary operations, even the commutative ones)

### Underscore keyword

The underscore `_` can be used to explicitly specify an empty slot where a pyramid could be. It is not particularly useful from the user point of view (maybe except for fine-tuning the position of the pyramids for code golf), but it is very helpful for the compiler. All the leaves are eventually terminated with `_`, and string expansion used the `_` keyword to help pack the code a bit better.

## Code optimisation

Psll compiler allows for some code optimisation. Optimising the code for speed would be, let's be honest with ourselves, a bit silly at this point. Psll optimisation attempts, therefore, to minimise number of bytes in the source code, such that the result can be used in [code golf challenges](https://codegolf.stackexchange.com/a/208938/68200).

### Greedy optimisation

Attempt to package each pair of root nodes in the abstract syntax tree. Insert an empty pyramid in the very first place which is beneficial (hence _greedy_). If all such places have been exhausted, try all teh possible insertions of a single pyramid.

This optimisation technique tends to result in tall pyramid scheme. It is very fast, and produces intermediate-quality results.

### Considerate optimisation

Consider all the possible places to either insert a single pyramid, or package two adjacent pyramids up to certain depth (10). Choose the most beneficial.

This optimisation technique tends to result in wide pyramid scheme. It is slower than the greedy optimisation, but very often results in a smaller pyramid scheme.

## ToDo's

This is not a real-purpose language. In this section the 'optimisation' refers to obtaining nicer-looking and more compact pyramids, *not* not efficient code.

- [ ] ?? Arrays / Linked lists
  - [x] Improve array implementation
  - [ ] `range` keyword
    - [ ] testing
    - [ ] re-checking
  - [ ] `len` keyword
- [ ] `nil` keyword
  - [ ] Make it more robustly than `(arg 999)`
  - [ ] ?? Allow compiler to insert `def`s into preamble
- [ ] Prettify the intermediate representation
- [ ] <s>?? `*( ... )` construct</s> probs no
  - [x] Add testing psll bash script to tests
    - [ ] <s>?? And somehow coverage</s> [`bashcov`](https://github.com/infertux/bashcov)
  - [ ] Use `hypothesis` in testing ?
  - [ ] Test for correct example output
  - [ ] ?? Test code optimisation
- [ ] ?? Tree rendering
  - [ ] ?? Have a look at (optionally!) using `anytree` package for visualisation
  - [ ] ?? Ascii art to LaTeX
- [ ] ?? Make `PsllSyntaxError` class do more
  - [ ] ?? Backtrace
  - [ ] ?? Or, I guess, rip it out and make it a normal `SyntaxError`
- [ ] ?? Move the command line code from psll.py to a bash script
- [ ] Protect `set` and maybe some other keywords from accidentally writing something like `(set (x (set y 1)) (# line))`. `def` is already protected like that, so why not `set`.
- [ ] `++` and `--` keywords (aka increment and decrement?)
More on the 'project management' front:

- [ ] ?? Easier to use installation. Maybe a makefile which makes a symlink in the correct place...
  - [ ] ?? `pip install psll` ...
  - [ ] ? Move testing to makefile
    - [ ] Make sure it works with travis
  - [ ] ??? brew tap. I mean, why not. Its not polluting the core with needless software if its just a tap...
- [ ] Configure flake8 and fight with it for a while
- [ ] ?? Same for mypy
- [ ] Make sure migration to travis.com (from travis.org) went fine (whenever that happens)
- [ ] Better testing
  - [ ] Improve test coverage
    - [x] Make the coverage count only the tests for that file
    - [x] tree_repr coverage
    - [ ] psll coverage
    - [x] Test *asymmetric* children in `tree_repr`
- [ ] `psll.sh` is a mess, therefore (amongst others) `run.sh` is a mess

## Done's

Bullet points get moved here from the above section when they get finished. (It's nice to keep a history of past ideas and goals)

- [x] Compiler optimisation takes a long time
- [x] !! Add memoisation to `build_tree`
- [x] More compiler optimisations
  - [x] !! Subtree packing <s><- !!! (work on this next!)</s>
  - [x] <s>Packing with null-tree snakes</s> kindof
  - [x] Better (non-greedy?) optimisation
  - [x] Variable name optimisation
    - [x] Automatic shortening
    - [x] Packing into the upper parts of the triangles
- [x] ?? Pre-compile code optimisations <s>Not sure what that would be though, tbh.</s>
  - [x] Move string expansion to pre-proc
  - [x] Move binary bracket expansion to pre-proc
  - [x] Move null-trees to pre-proc <s><- (work on this next, because it's broken...)</s>
- [x] Add option to force a node with one child to make it a right child
  - [x] ?? Add None (or None-like) values to the abstract syntax tree representation
  - [x] ?? Interpret `_` as not-a-tree
  - [x] Therefore optimise `chr` in string expansion
  - [x] <s>Also add this to the snake optimiser</s>
- [x] Redo tree / string parsing with paired delimiter matching
  - [x] <s>?? Have a look at `pyparsing` (`QuotedString`, `nestedExpr`)</s> <- No, because I want to keep this as vanilla python as possible.
- [x] ?? Syntactic sugar
  - [x] Simpler writing of strings
    - [x] Add support for escape characters
  - [x] Simpler writing of nested nil pyramids
  - [x] `def` keyword
  - [x] ?? `_` keyword
  - [x] Implicit expansion of `out` command, such that one can write `(out "j: " j " | k: " k newline)` and it gets expanded into a pile of `out` commands
  - [x] Expansion of `+` and `*` commands too
    - [x] Right and left-associative expansion


## Bugs

- [ ] `[`, `]` and `"` Pyramid-Scheme keywords are not working at all at the moment (they ought to be typed as `\[`, `\]` and `\"`) (It's ok. They're really nto that useful, but it would be nice if they did actually work too.)
- [ ] `arrays` example is putting in rouge commas into int literals
- [ ] `()` pop the scope stack
- [ ] <s>`(_)` breaks the compiler (Why would someone decide to write this though...?)</s> Ok, so this is not happening anymore, but I don't know why so I'm leaving it here to investigate.
- [ ] Bug in greedy optimisation for source code with one major tree
- [ ] Intermediate representation is ugly since the multiple spaces are gone. This is not really a bug, but would be nice to change.
- [ ] `def` replacer sometimes adds an extra pyramid


## Bugs no more

- [x] Strings do not support escape characters <s>(And maybe they never will! Ha! They're just sugar anyway...)</s> (Fine...)
- [x] <s>`compact` option breaks when `N`th triangle is wider than all the `1..N-1`s.</s>
- [x] `compact` option does nothing
- [x] Asymmetric children cause issues in `tree_repr` in `add_one_child`
- [x] `"` command doesn't work (it gets recognized as a psll string)
- [x] Multiple spaces in strings get squashed to one because the intermediate representation is oblivious of context and just `re`'s the entire source.