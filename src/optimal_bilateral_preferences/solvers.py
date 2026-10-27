from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy.optimize import minimize

from .problem import Problem
from .welfares import WELFARES

nash = WELFARES["nash"]
MAX_BRUTE_FORCE = 22


def get_all_selections(n: int) -> np.ndarray:
    """Generates an array of every binary choice vector of size n.

    Parameters
    ----------
    n : int
        The size of the binary choice vector.

    Returns
    -------
    np.ndarray
        The array of each possible choice.

    Raises
    ------
    ValueError
        If the size is too big.
    """
    if n > MAX_BRUTE_FORCE:
        raise ValueError("Too many to brute force")

    X = np.array([list(np.binary_repr(i, width=n)) for i in range(2**n)], dtype=int)
    return X


def get_efficiency_frontier(problem: Problem, num_points: int = 100):
    """Computes the efficiency frontier through complete enumeration.

    Parameters
    ----------
    problem : Problem
        The problem instance, i.e. the preferences and scoring.
    num_points : int, optional
        The number of points to take on the frontier, by default 100

    Returns
    -------
    _type_
        The complete list of scores on all possible preferences, and the x-y coordinates of the frontier.
    """
    X = get_all_selections(problem.num_policies)

    score0, score1 = problem.score(X)

    X_opt0 = (problem.m0 > 0).astype(int)
    X_opt1 = (problem.m1 > 0).astype(int)

    opt_for0 = problem.score(X_opt0)
    opt_for1 = problem.score(X_opt1)

    efficiency_front0 = []
    efficiency_front1 = []

    threshold0_range = np.linspace(opt_for1[0], opt_for0[0], num_points)
    for threshold0 in threshold0_range:
        score1_clipped = score1.copy()
        score1_clipped[score0 < threshold0] = -np.inf
        efficiency_front0.append(score0[np.argmax(score1_clipped)])
        efficiency_front1.append(score1[np.argmax(score1_clipped)])

    efficiency_front0 = np.array(efficiency_front0)
    efficiency_front1 = np.array(efficiency_front1)

    return (score0, score1), (efficiency_front0, efficiency_front1)


def naive(prefs: Problem, _=None) -> np.ndarray:
    """Naive optimisation of the problem.

    Parameters
    ----------
    prefs : Problem
        The problem to optimise.
    _ : _type_, optional
        The welfare function, unused, by default None

    Returns
    -------
    np.ndarray
        The binary choice vector.
    """
    return (prefs.m0 + prefs.m1 > 0).astype(int)


def brute_force(prefs: Problem, welfare=nash) -> np.ndarray:
    """Solves the problem with burte force, all combinations.

    Parameters
    ----------
    prefs : Problem
        The problem to solve
    welfare : Callable, optional
        The welfare to optimise, by default nash

    Returns
    -------
    np.ndarray
        The optimal binary choice vector.
    """
    X = get_all_selections(prefs.num_policies)
    return X[np.argmax(prefs.welfare(X, welfare))]


def greedy(problem: Problem, welfare: Callable = nash) -> np.ndarray:
    """Heuristically optimises the choice vector using a greedy approach.

    Parameters
    ----------
    problem : Problem
        The problem to solve.
    welfare : Callable, optional
        The welfare to optimise, by default nash

    Returns
    -------
    np.ndarray
        The heuristic optimal binary choice vector (not certainly optimal).
    """
    num_policies = problem.num_policies

    current_score0 = problem.b0
    current_score1 = problem.b1

    implemented_policies = []
    for _ in range(num_policies):
        best_policy = None
        best_welfare = welfare(current_score0, current_score1)
        for i in range(num_policies):
            if not i in implemented_policies:
                proposed_score0 = current_score0 + problem.m0[i]
                proposed_score1 = current_score1 + problem.m1[i]

                if welfare(proposed_score0, proposed_score1) > best_welfare:
                    best_welfare = welfare(proposed_score0, proposed_score1)
                    best_policy = i

        if best_policy is not None:
            implemented_policies.append(best_policy)
            current_score0 = current_score0 + problem.m0[best_policy]
            current_score1 = current_score1 + problem.m1[best_policy]
        else:
            break

    X_optimal_greedy = np.zeros(num_policies, dtype=int)
    for i in implemented_policies:
        X_optimal_greedy[i] = 1

    return X_optimal_greedy


def simulated_annealing(
    problem: Problem,
    welfare=nash,
    steps: int = 100_000,
    seed: int | None = None,
):
    """Heuristically optimises the choice vector using simulated annealing.

    Parameters
    ----------
    problem : Problem
        The problem to solve.
    welfare : Callable, optional
        The welfare to optimise, by default nash
    steps : int, optional
        The number of steps in the annealing, by default 100_000
    seed : int | None, optional
        The random seed for the annealing, by default None

    Returns
    -------
    tuple
        The history of the scores, and the heuristic optimal binary choice vector (not certainly optimal)
    """
    if seed is not None:
        np.random.seed(seed)

    num_policies = problem.num_policies
    delta_max = 2 * num_policies

    def cooling_schedule(k):
        return delta_max / (1 + k) ** 0.5

    X_current = np.zeros(num_policies)

    scores = []

    for k in range(steps):
        temperature = cooling_schedule(k)
        beta = 1 / temperature

        X_proposed = X_current.copy()
        proposed_flip = np.random.randint(0, num_policies)

        X_proposed[proposed_flip] = 1 - X_proposed[proposed_flip]

        current_score = welfare(*problem.score(X_current))
        proposed_score = welfare(*problem.score(X_proposed))
        delta = proposed_score - current_score
        accept_probability = np.exp(beta * delta)
        if np.random.uniform(0, 1) < accept_probability:
            X_current = X_proposed
            scores.append(proposed_score)
        else:
            scores.append(current_score)

    return scores, X_current


def relax(problem: Problem, welfare=nash) -> np.ndarray:
    """Solves the relaxed continuous version of the problem.

    Parameters
    ----------
    problem : Problem
        The problem instance to solve.
    welfare : Callabel, optional
        The welfare to optimise, by default nash

    Returns
    -------
    np.ndarray
        The relaxed optimal choice vector (not binary)
    """
    n = problem.num_policies
    result = minimize(
        lambda x: -problem.welfare(x, welfare),
        x0=np.full(n, 0.5),
        bounds=[(0, 1)] * n,
        method="L-BFGS-B",
    )
    return result.x


def continuous_relaxation(problem: Problem, welfare=nash) -> np.ndarray:
    """Heuristically solves the problem by clipping / rounding the relaxed solution.

    Parameters
    ----------
    problem : Problem
        The problem instance to solve
    welfare : Callable, optional
        The welfare function to optimise, by default nash

    Returns
    -------
    np.ndarray
        The heuristic optimal binary choice vector (not certainly optimal)
    """
    return (relax(problem, welfare) > 0.5).astype(int)


SOLVERS = {
    "naive": naive,
    "brute": brute_force,
    "greedy": greedy,
    "simulated": simulated_annealing,
    "relaxation": continuous_relaxation,
}


def solve(problem: Problem, welfare=nash, method: str = "naive") -> np.ndarray:
    """Helper to solve with different methods.

    Parameters
    ----------
    problem : Problem
        The problem instance to solve
    welfare : Callable, optional
        The welfare function to optimise, by default nash
    method : str, optional
        The method to use (...), by default "naive"

    Returns
    -------
    np.ndarray
        The binary soultion vector (with history for simulated annealing...)
    """
    return SOLVERS[method](problem, welfare)
