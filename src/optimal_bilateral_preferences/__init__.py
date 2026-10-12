"""Picking which way to go on a bunch of decisions when two people disagree.

A small side project. The problem setup lives in ``problem.py`` and the
different ways of solving it in ``solvers.py``.
"""

from .problem import Preferences, egalitarian, nash, simulate, utilitarian
from .solvers import (
    brute_force,
    continuous_relaxation,
    efficiency_frontier,
    greedy,
    naive,
    relax,
    simulated_annealing,
    solve,
)

__all__ = [
    "Preferences",
    "brute_force",
    "continuous_relaxation",
    "efficiency_frontier",
    "egalitarian",
    "greedy",
    "nash",
    "naive",
    "relax",
    "simulate",
    "simulated_annealing",
    "solve",
    "utilitarian",
]
