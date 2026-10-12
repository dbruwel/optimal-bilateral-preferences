import numpy as np
import pytest

from optimal_bilateral_preferences import (
    Preferences,
    brute_force,
    continuous_relaxation,
    greedy,
    naive,
    simulate,
    simulated_annealing,
    utilitarian,
)
from optimal_bilateral_preferences.cli import read_csv


def test_fifty_fifty_scores():
    prefs = Preferences.from_leans([0.7, 0.2], [0.4, 0.9])
    assert np.allclose(prefs.scores([0, 0]), (0.3 + 0.8, 0.6 + 0.1))
    assert np.allclose(prefs.scores([1, 0]), (0.7 + 0.8, 0.4 + 0.1))
    assert np.allclose(prefs.scores([1, 1]), (0.7 + 0.2, 0.4 + 0.9))


def test_leans_out_of_range():
    with pytest.raises(ValueError):
        Preferences.from_leans([1.5], [0.5])


def test_normalised_goes_from_zero_to_one():
    prefs = simulate(10, seed=1)
    norm = prefs.normalised()
    (worst0, best0), (worst1, best1) = norm.score_range()
    assert np.allclose([worst0, best0, worst1, best1], [0, 1, 0, 1])
    # Each person's own favourite selection is still their favourite.
    assert norm.scores((prefs.m0 > 0).astype(int))[0] == pytest.approx(1)


def test_naive_is_the_utilitarian_optimum():
    prefs = simulate(12, seed=3)
    x = naive(prefs)
    assert prefs.welfare(x, utilitarian) == pytest.approx(
        prefs.welfare(brute_force(prefs, utilitarian), utilitarian)
    )


def test_greedy_adds_the_policy_it_picked():
    # The notebook version added the last policy it looked at, not the best one.
    # When both people agree, it should just do what they both want.
    prefs = Preferences.from_leans([0.9, 0.8, 0.1], [0.9, 0.8, 0.1])
    assert list(greedy(prefs)) == [1, 1, 0]


def test_solvers_never_beat_brute_force():
    for seed in range(5):
        prefs = simulate(12, seed=seed)
        best = prefs.welfare(brute_force(prefs))
        for x in (
            greedy(prefs),
            simulated_annealing(prefs, steps=5_000, seed=seed),
            continuous_relaxation(prefs),
            naive(prefs),
        ):
            assert prefs.welfare(x) <= best + 1e-9


def test_annealing_finds_the_optimum_on_small_problems():
    prefs = simulate(10, seed=0)
    x = simulated_annealing(prefs, steps=20_000, seed=0)
    assert prefs.welfare(x) == pytest.approx(prefs.welfare(brute_force(prefs)))


def test_read_csv_with_percentages(tmp_path):
    path = tmp_path / "decisions.csv"
    path.write_text("decision,alice,bob\ncouch,90,40\ndog,20,95\n")
    prefs, people = read_csv(path)
    assert people == ["alice", "bob"]
    assert prefs.names == ["couch", "dog"]
    assert np.allclose(prefs.m0, [0.8, -0.6])
