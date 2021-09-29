---
layout: default
---

Performance tests of various parts of the [`psll-lang`](https://github.com/MarcinKonowalczyk/psll-lang).

## Tree building

### Pyramid.from_text

{% include figure2.html id="figure_1" data="./data/perf_pyramid_from_text.data" ylabel="execution time / us" scale="0.001" %}

### Tree.from_text

{% include figure.html id="figure_2" data="./data/perf_tree_from_text.data" ylabel="execution time / us" scale="0.001" color="132, 99, 255" %}

### Adding pyramids

Adding two pyramids side by side. Tested for pyramids containing all permutations of string, from empty to length 9.

{% include figure.html id="figure_3" data="./data/perf_add_side_by_side.data" ylabel="execution time / us" scale="0.001" color="99, 180, 255" %}
