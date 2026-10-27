from __future__ import annotations

import numpy as np

from .welfares import WELFARES


class Problem:
    """Problem object, containing the preferences of eeach person for each problem. In linear form."""

    def __init__(
        self,
        b0: float,
        b1: float,
        m0: np.ndarray,
        m1: np.ndarray,
        names: list[str] | None = None,
    ):
        self.b0 = b0
        self.b1 = b1
        self.m0 = np.asarray(m0, dtype=float)
        self.m1 = np.asarray(m1, dtype=float)
        self.names = names

        self.num_policies = len(self.m0)

        if self.m0.shape != self.m1.shape:
            raise ValueError("m0 and m1 need to be the same length")

    @classmethod
    def from_pref0(
        cls,
        agent0_pref0: np.ndarray,
        agent1_pref0: np.ndarray,
        names: list[str] | None = None,
    ) -> Problem:
        """Generates a problem statement from "50:50" preferences. That is, situations
        where someone says "I'm 70:30" for this decision, meaning I'm 70 against and 30 for.

        Parameters
        ----------
        agent0_pref0 : np.ndarray
            The preferences for the first person. This is the "against side".
        agent1_pref0 : np.ndarray
            The preferences for the second person.
        names : list[str] | None, optional
            The list of names of the decisions, by default None

        Returns
        -------
        Problem
            The problem object.
        """
        agent0_pref0 = np.asarray(agent0_pref0, dtype=float)
        agent1_pref0 = np.asarray(agent1_pref0, dtype=float)

        if np.any((agent0_pref0 < 0) | (agent0_pref0 > 1)):
            raise ValueError("Agent 0 preferences must be in [0, 1]")

        if np.any((agent1_pref0 < 0) | (agent1_pref0 > 1)):
            raise ValueError("Agent 1 preferences must be in [0, 1]")

        return cls(
            b0=(1 - agent0_pref0).sum(),
            b1=(1 - agent1_pref0).sum(),
            m0=2 * agent0_pref0 - 1,
            m1=2 * agent1_pref0 - 1,
            names=names,
        )

    def score(self, x):
        """Computes the score vector for a given choice set.

        Parameters
        ----------
        x : np.ndarray
            The binary vector of choices.

        Returns
        -------
        np.ndarray
            The score of each outcome.
        """
        x = np.asarray(x)
        return x @ self.m0 + self.b0, x @ self.m1 + self.b1

    def welfare(self, x, welfare=WELFARES["nash"]):
        s0, s1 = self.score(x)
        return welfare(s0, s1)


def generate_problem(num_policies: int, seed: int | None = 42) -> Problem:
    """Generates a random problem from a beta distribution. The prefferences are slightly missaligned.

    Parameters
    ----------
    num_policies : int
        The number of policies to generate.
    seed : int | None, optional
        A random seed, by default 42

    Returns
    -------
    Problem
        The problem object.
    """
    np.random.seed(42)
    agent0_pref0 = np.random.beta(1, 0.5, num_policies)
    agent1_pref0 = np.random.beta(0.5, 1, num_policies)

    return Problem.from_pref0(agent0_pref0, agent1_pref0)
