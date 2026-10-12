"""Different ways of picking which decisions to make.

Every solver takes a ``Preferences`` and returns a 0/1 selection vector. The
``welfare`` argument is any function of the two scores, see ``problem.py``.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from .problem import Preferences, nash

MAX_BRUTE_FORCE = 22


def all_selections(n: int) -> np.ndarray:
    """Every possible 0/1 selection of ``n`` decisions, shape ``(2**n, n)``."""
    if n > MAX_BRUTE_FORCE:
        raise ValueError(f"2**{n} selections is too many to brute force")
    return (np.arange(2**n)[:, None] >> np.arange(n)) & 1


def naive(prefs: Preferences) -> np.ndarray:
    """Go with whoever feels more strongly about each decision.

    This is the same as maximising the sum of the scores, and is what tends to
    happen in practice. The person with stronger opinions wins most things.
    """
    return (prefs.m0 + prefs.m1 > 0).astype(int)


def brute_force(prefs: Preferences, welfare=nash) -> np.ndarray:
    """Check every selection and return the best. Only feasible up to ~20 decisions."""
    X = all_selections(prefs.num_policies)
    return X[np.argmax(prefs.welfare(X, welfare))]


def efficiency_frontier(prefs: Preferences, num_points: int = 100):
    """Trace the efficiency frontier by brute force.

    For a range of thresholds on person 0's score, find the selection that
    gives person 1 the most while keeping person 0 above the threshold.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        Person 0 and person 1 scores along the frontier.
    """
    s0, s1 = prefs.scores(all_selections(prefs.num_policies))
    # Runs from "person 1 gets everything" to "person 0 gets everything".
    best_for_1 = (prefs.m1 > 0).astype(int)

    front0, front1 = [], []
    for threshold in np.linspace(prefs.scores(best_for_1)[0], s0.max(), num_points):
        clipped = np.where(s0 >= threshold, s1, -np.inf)
        i = np.argmax(clipped)
        front0.append(s0[i])
        front1.append(s1[i])
    return np.array(front0), np.array(front1)


def greedy(prefs: Preferences, welfare=nash, start=None) -> np.ndarray:
    """Greedily flip decisions to "yes" while it improves the welfare.

    Starting from ``start`` (all "no" by default), each step tries every
    decision that hasn't been flipped yet and keeps the one that improves the
    welfare the most. Stops when nothing helps.
    """
    n = prefs.num_policies
    x = np.zeros(n, dtype=int) if start is None else np.array(start, dtype=int)
    available = set(np.flatnonzero(x == 0))
    best_welfare = prefs.welfare(x, welfare)

    while available:
        candidates = sorted(available)
        trial = np.tile(x, (len(candidates), 1))
        trial[np.arange(len(candidates)), candidates] = 1
        trial_welfare = prefs.welfare(trial, welfare)

        best = np.argmax(trial_welfare)
        if trial_welfare[best] <= best_welfare:
            break
        x = trial[best]
        best_welfare = trial_welfare[best]
        available.remove(candidates[best])

    return x


def simulated_annealing(
    prefs: Preferences,
    welfare=nash,
    steps: int = 100_000,
    start_temperature: float | None = None,
    seed: int | None = None,
    history: bool = False,
):
    """Flip random decisions, sometimes accepting worse selections early on.

    The temperature cools like ``T_0 / sqrt(1 + k)``. A worse flip is accepted
    with probability ``exp(delta / T)``.

    Parameters
    ----------
    start_temperature : float, optional
        Defaults to the biggest change a single flip makes to the welfare from
        the starting point, so it scales with whatever welfare you use.
    history : bool, optional
        If True, also return the welfare after every step.

    Returns
    -------
    numpy.ndarray or tuple[numpy.ndarray, list[float]]
        The best selection seen (and the history, if asked for).
    """
    rng = np.random.default_rng(seed)
    n = prefs.num_policies
    x = np.zeros(n, dtype=int)
    current = prefs.welfare(x, welfare)

    if start_temperature is None:
        single_flips = prefs.welfare(np.eye(n, dtype=int), welfare)
        start_temperature = np.abs(single_flips - current).max()
    best_x, best = x.copy(), current
    scores = []

    for k in range(steps):
        temperature = start_temperature / (1 + k) ** 0.5
        flip = rng.integers(n)
        x[flip] = 1 - x[flip]
        proposed = prefs.welfare(x, welfare)

        delta = proposed - current
        if delta >= 0 or rng.uniform() < np.exp(delta / temperature):
            current = proposed
            if current > best:
                best_x, best = x.copy(), current
        else:
            x[flip] = 1 - x[flip]
        scores.append(current)

    return (best_x, scores) if history else best_x


def relax(prefs: Preferences, welfare=nash) -> np.ndarray:
    """Solve the continuous version, where each decision can be anywhere in [0, 1].

    For Nash welfare this is a (non-convex) quadratic with box constraints.
    Here it's just handed to scipy.
    """
    n = prefs.num_policies
    result = minimize(
        lambda x: -prefs.welfare(x, welfare),
        x0=np.full(n, 0.5),
        bounds=[(0, 1)] * n,
        method="L-BFGS-B",
    )
    return result.x


def continuous_relaxation(prefs: Preferences, welfare=nash) -> np.ndarray:
    """Solve the continuous version and round it to the nearest selection."""
    return (relax(prefs, welfare) > 0.5).astype(int)


SOLVERS = {
    "brute": brute_force,
    "greedy": greedy,
    "annealing": simulated_annealing,
    "relaxation": continuous_relaxation,
}


def solve(prefs: Preferences, welfare=nash, method: str = "auto") -> np.ndarray:
    """Pick a selection, brute forcing if it's small enough and greedy otherwise."""
    if method == "naive":
        return naive(prefs)
    if method == "auto":
        method = "brute" if prefs.num_policies <= 20 else "greedy"
    return SOLVERS[method](prefs, welfare)
