# 👩🏻‍💻 psll-lang development <!-- omit in toc -->

Notes for developers.

---

- [ToDo's](#ToDos)
- [Done's](#Dones)
- [Bugs](#Bugs)
- [Bugs no more](#Bugs-no-more)

## General

Run the checks on the code with:

```
pip install -Uq flake8 mypy black
black --preview .
flake8 .
mypy .
```

or with pre-commit:

```
pip install -Uq pre-commit
pre-commit run --all-files
```

Install psll in an editable mode:

```
pip install -e .
```

## ToDo's

This is not a real-purpose language. In this section the 'optimisation' refers to obtaining nicer-looking and more compact pyramids, *not* not efficient code.

- [ ] ?? Arrays / Linked lists
  - [x] Improve array implementation
  - [ ] `range` keyword
    - [ ] add testing thereof
  - [ ] `len` keyword
- [ ] `nil` keyword
  - [ ] Make it more robustly than `(arg 999)`
  - [ ] ?? Allow compiler to insert `def`s into preamble
- [ ] Prettify the intermediate representation
- [ ] <s>?? `*( ... )` construct</s> probs no
- [ ] ?? Tree rendering
  - [ ] ?? Have a look at (optionally!) using `anytree` package for visualisation
  - [ ] ?? Ascii art to LaTeX
- [ ] ?? Make `PsllSyntaxError` class do more
  - [ ] ?? Backtrace
  - [ ] ?? Or, I guess, rip it out and make it a normal `SyntaxError`
- [ ] Protect `set` and maybe some other keywords from accidentally writing something like `(set (x (set y 1)) (# line))`. `def` is already protected like that, so why not `set`.
- [ ] `++` and `--` keywords (aka increment and decrement?)
- [ ] Expanders shouldn't mutate nodes!
  - [ ] @functional decorator? Is that a thing?
- [ ] Make string expansion balanced binary
  - [ ] ? should this be a compiler option...
- [ ] ? allow only letters and numbers in variable names
- [ ] ? Actually throw an error if bracket is found in an array, or is this somehow, sometimes desired? After all, braces are not allowed in variable names.
- [ ] Add more sorting algorithms to examples (because they're fun to code.) Pancake sort?
  - [ ] ? Add something to help with prefix and suffix?
- [ ] Allow one to write the empty pyramid keyword explicitly as the underscore, such that `( (a) (b) )` can also be written as `(_ (a) (b) )`, just for completeness.
- [ ] Add section about array expansions to this README
- [ ] Comments between the pyramids (using inverted trees...?)
  - [x] Check whether it would even work... (it would!!!)
  - [ ] Make sure they don't bloat the code...? (don't appear on the right)
  - [ ] Make sure they appear roughly in the right place...?
- [ ] Put all the trees under a single root??
- [ ] Add Ewok-village optimisation (<- this is a *big* one. should probably make it version 2.0.0)


More on the 'project management' front:

- [ ] ?? Easier to use installation. Maybe a makefile which makes a symlink in the correct place...
  - [x] ?? `pip install psll` ...
  - [ ] ??? brew tap. I mean, why not. Its not polluting the core with needless software if its just a tap...
  - [x] finish the `download-pyra` option in psll cli
- [x] Make sure migration to travis.com (from travis.org) went fine (whenever that happens)
  - [ ] ?? deprecate travis?? github actions seem to work better for small projects like this
- [ ] Better testing
  - [ ] Add testing psll bash script to tests
    - [ ] <s>?? And somehow coverage</s> [`bashcov`](https://github.com/infertux/bashcov)
    - [ ] Use `hypothesis` in testing ?
    - [ ] Test for correct example output
    - [ ] ?? Test code optimisation
  - [ ] Improve test coverage
    - [x] Make the coverage count only the tests for that file
    - [x] tree_repr coverage
    - [ ] psll coverage
    - [x] Test *asymmetric* children in `tree_repr`
  - [ ] ? Move testing to makefile
    - [ ] Make sure it works with travis
  - [ ] Move to pytest
  - [ ] Test cli
- [ ] Add esolang wiki page. I think I deserve one now.
- [ ] Add psll to tio...?
- [ ] Add more thorough mypy checks
- [x] Add to PyPi


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
- [x] Add mention of the Sigbovik paper to README
- [x] <s>?? Move the command line code from psll.py to a bash script</s> (<- not done in favour of abandoning the bash script alltogether)
- [x] Configure flake8 and fight with it for a while
- [x] ?? Same for mypy
- [x] `psll.sh` is a mess, therefore (amongst others) `run.sh` is a mess


## Bugs

- [ ] `[`, `]` and `"` Pyramid-Scheme keywords are not working at all at the moment (they ought to be typed as `\[`, `\]` and `\"`) (It's ok. They're really nto that useful, but it would be nice if they did actually work too.)
- [ ] `arrays` example is putting in rouge commas into int literals
- [ ] `()` pop the scope stack
- [ ] <s>`(_)` breaks the compiler (Why would someone decide to write this though...?)</s> Ok, so this is not happening anymore, but I don't know why so I'm leaving it here to investigate.
- [ ] Bug in greedy optimisation for source code with one major tree
- [ ] Intermediate representation is ugly since the multiple spaces are gone. This is not really a bug, but would be nice to change.
- [ ] `def` replacer sometimes adds an extra pyramid
- [ ] ? should `( (x) (y z) )` and `( x (y z) )` have the same intermediate ast?
- [x] The order of operations in right-associative expansions is reversed in the last bracket!!


## Bugs no more

- [x] Strings do not support escape characters <s>(And maybe they never will! Ha! They're just sugar anyway...)</s> (Fine...)
- [x] <s>`compact` option breaks when `N`th triangle is wider than all the `1..N-1`s.</s>
- [x] `compact` option does nothing
- [x] Asymmetric children cause issues in `tree_repr` in `add_one_child`
- [x] `"` command doesn't work (it gets recognized as a psll string)
- [x] Multiple spaces in strings get squashed to one because the intermediate representation is oblivious of context and just `re`'s the entire source.
