"""Split a list of decisions between two people from a CSV.

The CSV needs a ``decision`` column and one column per person, holding how
much they lean towards "yes" (either 0 to 1, or 0 to 100). For example:

    decision,alice,bob
    couch under the window,0.9,0.4
    get a dog,0.2,0.95

Run with ``bilateral decisions.csv`` (after ``pip install -e .``).
"""

from __future__ import annotations

import argparse
import csv

import numpy as np

from .problem import WELFARES, Preferences
from .solvers import naive, solve


def read_csv(path: str):
    """Read a decisions CSV, returning the preferences and the two people's names."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        people = [column for column in reader.fieldnames if column != "decision"]
        if "decision" not in reader.fieldnames or len(people) != 2:
            raise ValueError("need a 'decision' column and exactly two people")
        rows = list(reader)

    names = [row["decision"] for row in rows]
    leans = np.array([[float(row[p]) for p in people] for row in rows])
    if leans.max() > 1:
        leans = leans / 100

    return Preferences.from_leans(leans[:, 0], leans[:, 1], names=names), people


def report(prefs: Preferences, x, people) -> None:
    """Print each decision and how both people come out of it.

    Scores are shown out of the number of decisions, plus as a percentage of
    the way from each person's worst case to their best case.
    """
    width = max(len(name) for name in prefs.names)
    lean0 = (prefs.m0 + 1) / 2
    lean1 = (prefs.m1 + 1) / 2

    print(f"{'':{width}}  {people[0]:>8}  {people[1]:>8}")
    for name, a, b, choice in zip(prefs.names, lean0, lean1, x):
        print(f"{name:{width}}  {a:>8.0%}  {b:>8.0%}   -> {'yes' if choice else 'no'}")

    n = prefs.num_policies
    norm = prefs.normalised()

    def summary(x):
        s0, s1 = prefs.scores(x)
        r0, r1 = norm.scores(x)
        return f"{people[0]} {s0:.1f}/{n} ({r0:.0%}), {people[1]} {s1:.1f}/{n} ({r1:.0%})"

    print()
    print(f"this split:                     {summary(x)}")
    print(f"going with whoever cares more:  {summary(naive(prefs))}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pick which way to go on a list of decisions so both people are happy."
    )
    parser.add_argument("csv", help="CSV with a 'decision' column and one per person")
    parser.add_argument(
        "--welfare", choices=WELFARES, default="nash", help="what to optimise"
    )
    parser.add_argument(
        "--method",
        choices=["auto", "brute", "greedy", "annealing", "relaxation", "naive"],
        default="auto",
        help="solver to use (auto brute forces up to 20 decisions)",
    )
    parser.add_argument(
        "--normalise",
        action="store_true",
        help="score everyone from 0 (worst case) to 1 (best case) before optimising",
    )
    args = parser.parse_args()

    prefs, people = read_csv(args.csv)
    target = prefs.normalised() if args.normalise else prefs
    x = solve(target, WELFARES[args.welfare], method=args.method)
    report(prefs, x, people)


if __name__ == "__main__":
    main()
