# psll-lang

[![Build Status](https://travis-ci.org/MarcinKonowalczyk/psll-lang.svg?branch=master)](https://travis-ci.org/MarcinKonowalczyk/psll-lang) [![Coverage Status](https://coveralls.io/repos/github/MarcinKonowalczyk/psll-lang/badge.svg?branch=master)](https://coveralls.io/github/MarcinKonowalczyk/psll-lang?branch=master)

A lisp-like language which compiles to [pyramid scheme](https://github.com/ConorOBrien-Foxx/Pyramid-Scheme) (**p**yramid **s**cheme **l**isp-**l**ike syntax, aka `psll`).

## Installation

Make  `psll.py` executable:

```
chmod u+x psll.py
```
or use the `psll` bash script (which you might want to edit to make it point to the correct files) which compiles and runs a program.

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

N.b. C# highlighting seems to look fine for most intensions and purposes (at lest in vscode). Lisp-highlighting somehow looks worse in my opinion.

```cs
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

or with the `psll` bash script:

```
./psll ./examples/nargin_counter.psll 4 3 5 2 4
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

### Underscore keyword

The underscore `_` can be used to explicitly specify an empty slot where a pyramid could be. It is not particularly useful from the user point of view (maybe except for fine-tuning the position of the pyramids for code golf), but it is very helpful for the compiler. All the leaves are eventually terminated with `_`, and string expansion used the `_` keyword to help pack the code a bit better.

## ToDo's

This is not a real-purpose language. In this section the 'optimisation' refers to obtaining nicer-looking and more compact pyramids, *not* not efficient code.

- [ ] More compiler optimisations
  - [x] !! Subtree packing <s><- !!! (work on this next!)</s>
  - [x] <s>Packing with null-tree snakes</s> kindof
  - [ ] Better (non-greedy?) optimisation
  - [ ] Variable name optimisation
    - [ ] Automatic shortening
    - [x] Packing into the upper parts of the triangles
- [x] ?? Pre-compile code optimisations <s>Not sure what that would be though, tbh.</s>
  - [x] Move string expansion to pre-proc
  - [x] Move binary bracket expansion to pre-proc
  - [x] Move null-trees to pre-proc <s><- (work on this next, because it's broken...)</s>
- [x] ?? Syntactic sugar
  - [x] Simpler writing of strings
    - [ ] Add support for escape characters
  - [x] Simpler writing of nested nil pyramids
  - [x] `def` keyword
  - [x] ?? `_` keyword
  - [ ] ?? Arrays / Linked lists
- [x] Compiler optimisation takes a long time
- [ ] ?? Easier to use installation. Maybe a make-script which makes a symlink in the correct place...
- [ ] Improve test coverage
  - [x] Make the coverage count only the tests for that file
  - [x] tree_repr coverage
  - [ ] psll coverage
- [ ] ?? Tree rendering
  - [ ] ?? Have a look at (optionally!) using `anytree` package for visualisation
  - [ ] ?? Ascii art to LaTeX
- [ ] ?? Make PsllSyntaxError class do more
  - [ ] ?? Backtrace
- [x] Add testing psll bash script to tests
  - [ ] ?? And somehow coverage
- [x] Add option to force a node with one child to make it a right child
  - [x] ?? Add None (or None-like) values to the abstract syntax tree representation
  - [x] ?? Interpret `_` as not-a-tree
  - [x] Therefore optimise `chr` in string expansion
  - [ ] Also add this to the snake optimiser
- [x] !! Add memoisation to `build_tree`

## Bugs
- [x] <s>`compact` option breaks when `N`th triangle is wider than all the `1..N-1`s.</s>
- [x] `compact` option does nothing
- [ ] Strings do not support escape characters (And maybe they never will! Ha! They're just sugar anyway...)
- [ ] `(_)` breaks the compiler (Why would someone decide to write this though...?)