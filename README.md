# psll-lang performance page

Github pages branch for displaying performance of `psll`. This is a bit of an experiment, to see how to add performance analysis to the CI toolchain.

Page built with [jekyll](). Theme based on [no-style-please](https://github.com/riggraz/no-style-please).

## Local build

To build and serve the website locally, run:

```
bundle clean
bundle install
bundle exec jekyll serve --incremental
```

```
cat result.perf | tail -n +2 | awk -v sha=$GITHUB_SHA '{ f = "./data/" $1 ".data"; $1 = sha; print >> f }'
```