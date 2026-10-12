# Optimal Bilateral Preferences

> **A note on how this was made**: I wrote the original code and analysis in 2025. In October 2026 I came back to it to clean up and, with help from AI tools, restructured it into a package, added tests, docstrings and this write-up, so that anyone reading it can follow what I was thinking. That's why a large part of the repo arrives in one large commit. The ideas, original code and logic, results, and any mistakes are mine.

This started when moving in with someone. There are lots of little decisions (where the couch goes, where the pots live) and it's easy for whoever has stronger opinions to win every one of them, so the other person isn't generally happy with how things end up. So, given a list of yes/no decisions and how two people feel about each, which split is best for *both* of them?

The same thing applies to anything with two sides picking between a bunch of options, like policies affecting two groups.

**Summary:** maximise the product of their scores (Nash welfare) on the scores people actually give. If one person is relaxed because they genuinely don't mind, that already gives a sensible split. If they do mind but don't say so, normalising each person (0 is their worst case, 1 is their best) evens things out, but it's a modelling choice with some real downsides, so it's an option rather than the default. Actually finding the best split is easy. Brute force works up to ~20 decisions and greedy is near enough optimal past that.

![Moving in: on the raw scale the relaxed person barely gets anything, normalised they both do about as well](notes/img/moving-in.png)

The full write-up is in [notes/findings.md](notes/findings.md), and the notebook [notebooks/main.ipynb](notebooks/main.ipynb) has the code behind every number and plot.

## Usage

Make a CSV with a `decision` column and one column for each person, saying how much they lean towards "yes" (0 to 1, or 0 to 100). "70" means "I'm 70:30 in favour".

```text
decision,alice,bob
couch under the window,0.95,0.40
get a dog,0.95,0.35
blinds instead of curtains,0.10,0.65
...
```

Then:

```bash
pip install -e .
bilateral examples/moving_in.csv
```

```text
                               alice       bob
couch under the window           95%       40%   -> yes
bed against the far wall         90%       45%   -> yes
pots in the bottom drawer         5%       55%   -> no
tv in the bedroom                10%       60%   -> no
get a dog                        95%       35%   -> yes
...

this split:                     alice 10.2/12 (92%), bob 5.3/12 (18%)
going with whoever cares more:  alice 10.9/12 (100%), bob 4.9/12 (0%)
```

The percentages are how far each person is from their worst case (0%) to their best case (100%). Bob is fairly relaxed about everything, so on the raw scores he doesn't get much. If that's because he's underselling how much he cares, adding `--normalise` yields:

```text
this split:                     alice 7.0/12 (60%), bob 6.3/12 (64%)
going with whoever cares more:  alice 10.9/12 (100%), bob 4.9/12 (0%)
```

[notes/findings.md](notes/findings.md#normalising) goes through when that's worth doing and when it isn't. Other options:

```bash
bilateral decisions.csv --normalise             # Nash welfare on min-max normalised scores
bilateral decisions.csv --welfare egalitarian   # or utilitarian
bilateral decisions.csv --method greedy         # brute, greedy, annealing, relaxation, naive
```

## How it works

Each person's score uses the "50:50 rule": if they're 70:30 in favour of something, doing it gives them 0.7 and not doing it gives them 0.3. Their total score is the sum over every decision, so it's linear in the selection:

$$s_a(\pi) = b_a + m_a \cdot \pi$$

The goal is to pick the 0/1 vector $\pi$ that maximises $s_0 s_1$ (same as $\ln s_0 + \ln s_1$). There are a few solvers in `solvers.py`:

- **brute force**, check all $2^n$ selections.
- **greedy**, keep flipping whichever decision helps most until nothing does.
- **simulated annealing**, random flips, sometimes accepting worse ones early on.
- **continuous relaxation**, let each decision be anywhere in $[0, 1]$, solve that, round.

## In Python

```python
from optimal_bilateral_preferences import Preferences, simulate, solve

prefs = Preferences.from_leans([0.95, 0.9, 0.1], [0.4, 0.45, 0.65])
x = solve(prefs)  # brute force up to 20 decisions, greedy after that
print(x, prefs.scores(x))

x = solve(prefs.normalised())  # same, on min-max normalised scores

prefs = simulate(30)  # two random people who mostly disagree
```

To run the notebook or the tests:

```bash
pip install -e ".[notebook,dev]"
jupyter lab notebooks/main.ipynb
pytest
```

## Repository layout

```text
optimal-bilateral-preferences/
├── examples/
│   └── moving_in.csv       # the example above
├── notebooks/
│   └── main.ipynb          # the exploration: frontier, solvers, comparisons
├── notes/
│   ├── findings.md         # the write-up
│   └── img/                # figures exported from the notebook
├── src/
│   └── optimal_bilateral_preferences/
│       ├── __init__.py
│       ├── cli.py          # the `bilateral` command
│       ├── problem.py      # preferences, scores and welfare functions
│       └── solvers.py      # brute force, greedy, annealing, relaxation
├── tests/
│   └── test_solvers.py
├── LICENSE
├── README.md
└── pyproject.toml
```

## License

MIT License. See the [LICENSE](LICENSE) file for details.
