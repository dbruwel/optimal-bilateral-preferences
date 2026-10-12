from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Preferences:
    """Two people's preferences over a collection of yes/no decisions.

    A selection ``x`` is a 0/1 vector with one entry per decision (1 = do it).
    Each person's score is linear in the selection:

        s_a(x) = b_a + m_a @ x

    Parameters
    ----------
    b0, b1 : float
        Each person's score if every decision is a "no".
    m0, m1 : numpy.ndarray
        How much each person's score changes when a decision flips to "yes".
    names : list[str], optional
        Names for the decisions, only used for printing.
    """

    b0: float
    b1: float
    m0: np.ndarray
    m1: np.ndarray
    names: list[str] | None = None

    def __post_init__(self):
        self.m0 = np.asarray(self.m0, dtype=float)
        self.m1 = np.asarray(self.m1, dtype=float)
        if self.m0.shape != self.m1.shape:
            raise ValueError("m0 and m1 need to be the same length")

    @classmethod
    def from_leans(cls, lean0, lean1, names=None) -> Preferences:
        """Build preferences using the "50:50 rule".

        For each decision, each person says how much they lean towards doing
        it, e.g. 0.7 for "I'm 70:30 in favour". Doing it gives them 0.7, not
        doing it gives them 0.3.

        Parameters
        ----------
        lean0, lean1 : array-like
            Each person's lean towards "yes" for every decision, in [0, 1].
        names : list[str], optional
            Names for the decisions.
        """
        lean0 = np.asarray(lean0, dtype=float)
        lean1 = np.asarray(lean1, dtype=float)
        if np.any((lean0 < 0) | (lean0 > 1)) or np.any((lean1 < 0) | (lean1 > 1)):
            raise ValueError("leans need to be between 0 and 1")

        return cls(
            b0=(1 - lean0).sum(),
            b1=(1 - lean1).sum(),
            m0=2 * lean0 - 1,
            m1=2 * lean1 - 1,
            names=names,
        )

    @property
    def num_policies(self) -> int:
        return len(self.m0)

    def score_range(self):
        """Return each person's (worst, best) possible score."""
        worst0 = self.b0 + np.minimum(self.m0, 0).sum()
        best0 = self.b0 + np.maximum(self.m0, 0).sum()
        worst1 = self.b1 + np.minimum(self.m1, 0).sum()
        best1 = self.b1 + np.maximum(self.m1, 0).sum()
        return (worst0, best0), (worst1, best1)

    def normalised(self) -> Preferences:
        """Rescale so each person scores 0 in their worst case and 1 in their best.

        Someone with mild opinions only has a narrow range of possible scores,
        so on the raw scale their whole range barely registers next to someone
        with strong opinions. Normalising puts everyone on "how close am I to
        getting everything I want".
        """
        (worst0, best0), (worst1, best1) = self.score_range()
        range0, range1 = best0 - worst0, best1 - worst1
        if range0 == 0 or range1 == 0:
            raise ValueError("someone doesn't care about anything, can't normalise")
        return Preferences(
            b0=(self.b0 - worst0) / range0,
            b1=(self.b1 - worst1) / range1,
            m0=self.m0 / range0,
            m1=self.m1 / range1,
            names=self.names,
        )

    def scores(self, x):
        """Return both people's scores for a selection.

        ``x`` can be a single selection of shape ``(n,)`` or a stack of them
        with shape ``(k, n)``, in which case you get arrays back.
        """
        x = np.asarray(x)
        return x @ self.m0 + self.b0, x @ self.m1 + self.b1

    def welfare(self, x, welfare=None):
        """Return the welfare of a selection (Nash welfare unless told otherwise)."""
        welfare = welfare or nash
        return welfare(*self.scores(x))


def nash(s0, s1):
    """Product of the scores, same as maximising log(s0) + log(s1).

    This is the default. Log is the scale-invariant (constant relative risk
    aversion) utility, so nobody gains by inflating their numbers, and a
    person near zero drags the whole thing down.
    """
    return s0 * s1


def utilitarian(s0, s1):
    """Sum of the scores. This is the "naive" go-with-whoever-cares-more option."""
    return s0 + s1


def egalitarian(s0, s1):
    """The worse-off person's score."""
    return np.minimum(s0, s1)


WELFARES = {"nash": nash, "utilitarian": utilitarian, "egalitarian": egalitarian}


def simulate(num_policies: int, seed: int | None = 42) -> Preferences:
    """Simulate two people who mostly disagree.

    Leans are drawn from beta distributions skewed in opposite directions, so
    person 0 tends to want "no" and person 1 tends to want "yes", with a fair
    few strong opinions mixed in.
    """
    rng = np.random.default_rng(seed)
    lean0 = 1 - rng.beta(1, 0.5, num_policies)
    lean1 = 1 - rng.beta(0.5, 1, num_policies)
    return Preferences.from_leans(lean0, lean1)
