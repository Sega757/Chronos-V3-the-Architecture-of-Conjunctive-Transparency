import pytest
import numpy as np
import warnings
import sys
import os

# Add sccs_core directory to sys.path so arbiter module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from arbiter import calculate_shannon_entropy, calculate_dcu_variance, MetaArbiter


class TestCalculateShannonEntropy:
    @pytest.mark.parametrize(
        "probabilities, expected",
        [
            ([1.0, 0.0], 0.0),
            ([0.5, 0.5], 1.0),
            ([0.25, 0.25, 0.25, 0.25], 2.0),
            ([0.0, 1.0, 0.0], 0.0),
            ([], 0.0),
        ],
    )
    def test_shannon_entropy_known_values(self, probabilities, expected):
        res = calculate_shannon_entropy(probabilities)
        assert res == pytest.approx(expected, rel=1e-6, abs=1e-9)

    def test_shannon_entropy_zero_handling(self):
        # Ensure zero probabilities don't trigger invalid log warnings or NaN
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.simplefilter("always")
            res = calculate_shannon_entropy([0.0, 0.0, 1.0])
            assert res == pytest.approx(0.0, rel=1e-6, abs=1e-9)
            assert len(recorded_warnings) == 0


class TestCalculateDCUVariance:
    def test_empty_embeddings(self):
        assert calculate_dcu_variance([]) == 0.0
        assert calculate_dcu_variance(None) == 0.0

    def test_identical_vectors(self):
        embeddings = [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
        var = calculate_dcu_variance(embeddings)
        assert var == pytest.approx(0.0, rel=1e-6, abs=1e-9)

    def test_opposite_vectors(self):
        embeddings = [[1.0, 0.0], [-1.0, 0.0]]
        var = calculate_dcu_variance(embeddings)
        assert var == pytest.approx(1.0, rel=1e-6, abs=1e-9)

    def test_zero_vectors(self):
        # Zero vectors normalize to zero, resulting in a zero mean vector and variance = 1.0
        embeddings = [[0.0, 0.0], [0.0, 0.0]]
        var = calculate_dcu_variance(embeddings)
        assert var == pytest.approx(1.0, rel=1e-6, abs=1e-9)


class TestMetaArbiter:
    def test_heuristic_fast_path(self):
        arbiter = MetaArbiter(tau_high=2.20, dcu_jailbreak=0.65)
        # Entropy for [0.5, 0.5] is 1.0 (< 2.20), DCU is 0 (< 0.65), prm_score is 1.0 (>= 0.80)
        state, entropy, dcu = arbiter.evaluate_state([0.5, 0.5], embeddings=None, prm_score=1.0)
        assert state == "HEURISTIC_FAST_PATH"
        assert entropy == pytest.approx(1.0, rel=1e-6, abs=1e-9)
        assert dcu == 0.0

    def test_linguistic_facade_dcu_jailbreak(self):
        arbiter = MetaArbiter(tau_high=2.20, dcu_jailbreak=0.65)
        opposite_embeddings = [[1.0, 0.0], [-1.0, 0.0]]  # DCU variance = 1.0 > 0.65
        state, entropy, dcu = arbiter.evaluate_state([0.5, 0.5], embeddings=opposite_embeddings, prm_score=1.0)
        assert state == "LINGUISTIC_FACADE"
        assert dcu == pytest.approx(1.0, rel=1e-6, abs=1e-9)

    @pytest.mark.parametrize(
        "probabilities, prm_score, expected_state",
        [
            # High entropy (> 2.20) -> [0.125]*8 has entropy = 3.0
            ([0.125] * 8, 1.0, "METACOGNITIVE_PAUSE"),
            # Low prm_score (< 0.80)
            ([0.5, 0.5], 0.79, "METACOGNITIVE_PAUSE"),
            # Exact boundary cutoff for prm_score (0.80) -> HEURISTIC_FAST_PATH
            ([0.5, 0.5], 0.80, "HEURISTIC_FAST_PATH"),
        ],
    )
    def test_metacognitive_pause_thresholds(self, probabilities, prm_score, expected_state):
        arbiter = MetaArbiter(tau_high=2.20, dcu_jailbreak=0.65)
        state, entropy, dcu = arbiter.evaluate_state(probabilities, embeddings=None, prm_score=prm_score)
        assert state == expected_state
