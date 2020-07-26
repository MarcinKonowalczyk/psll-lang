# lisp-like-to-pyramid-scheme

Compile pyramid scheme lisp-like (psll) syntax to full [pyramid scheme](https://github.com/ConorOBrien-Foxx/Pyramid-Scheme).

## Installation

Make  `ll2pyra` executable:
```
chmod u+x ll2pyra.py
```

## Use

Read the help:
```
./ll2pyra.py -h
```

Verbose output and save to the file:
```
./ll2pyra.py  array_sum_golf.psll -v -o
```

## Examples

The following is an example lisp-like pyramid scheme which counts the number of input arguments it gets, and then prints it out to the command line. The syntax supports `//` comments and newlines, as well as (almost) random additions of whitespace.

N.b. C# highlighting seems to look fine for most intensions and purposes (at lest in vscode).

```cs
// Count the number of input arguments

(set nil (arg 99)) // Make nil

// Count the number of input arguments - n
(set nargin 0)
(do
    cond
    (
        (set nargin (+ nargin 1))
        (set cond (! (= (arg nargin) nil)))
    )
)
(set nargin (- nargin 1))

// Print 'nargin: #'
((out (chr 110) (chr 97)) (out (chr 114) (chr 103)))
((out (chr 105) (chr 110)) (out (chr 58) (chr 32)))
(out nargin)
```

It can be compiled and run as follows:

```
./ll2pyra.py nargin_counter.psll -o -f
ruby ./Pyramid-Scheme/pyra.rb nargin_counter.pyra 4 3 5 2 4
```
The output is `nargin: 5`

## ToDo's

- [ ] More compiler optimisations, especially on the subtree level
  - [ ] Nil-tree snake optimisation
  - [ ] Variable name length optimisation
  - [ ] Variable stuffing optimisation
- [ ] Precompile code optimisations??
- [ ] Syntactic sugar?
  - [ ] Simpler writing of strings
  - [ ] Simpler writing of nested null pyramids