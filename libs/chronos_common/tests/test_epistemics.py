"""Tests for chronos_common.epistemics module."""

import math
import numpy as np
import pytest

from chronos_common.epistemics import (
    EpistemicState,
    shannon_entropy,
    vmf_concentration,
)


class TestShannonEntropy:
    """Test suite for shannon_entropy calculation."""

    @pytest.mark.parametrize(
        "probabilities, expected",
        [
            # Degenerate / Certainty distribution: H(X) = 0.0
            ([1.0], 0.0),
            ([1.0, 0.0, 0.0], 0.0),
            ([0.0, 0.0, 1.0, 0.0], 0.0),
            # Uniform distributions: H(X) = log2(N)
            ([0.5, 0.5], 1.0),
            ([0.25, 0.25, 0.25, 0.25], 2.0),
            ([1.0 / 8.0] * 8, 3.0),
            # Non-normalized inputs (should be normalized internally)
            ([2.0, 2.0], 1.0),
            ([10.0, 0.0], 0.0),
            # Arbitrary distribution
            ([0.5, 0.25, 0.25], 1.5),
        ],
    )
    def test_shannon_entropy_valid_cases(
        self, probabilities: list[float], expected: float
    ):
        result = shannon_entropy(probabilities)
        assert result == pytest.approx(expected, rel=1e-6, abs=1e-9)

    def test_shannon_entropy_zero_probability_convention(self):
        """Verify 0 log 0 = 0 convention and no warnings/errors on zeros."""
        probs = [0.5, 0.0, 0.5, 0.0]
        result = shannon_entropy(probs)
        assert result == pytest.approx(1.0, rel=1e-6, abs=1e-9)

    @pytest.mark.parametrize(
        "invalid_probs",
        [
            [],
            [0.0, 0.0],
            [-1.0, 0.5],
            [-0.1],
        ],
    )
    def test_shannon_entropy_invalid_inputs(self, invalid_probs: list[float]):
        with pytest.raises(
            ValueError, match="shannon_entropy: probabilities must sum to > 0"
        ):
            shannon_entropy(invalid_probs)


class TestVMFConcentration:
    """Test suite for vmf_concentration parameter estimation."""

    def test_vmf_concentration_aligned_vectors(self):
        """Highly aligned vectors on (p-1)-sphere should yield high kappa."""
        vectors = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        kappa = vmf_concentration(vectors)
        assert kappa > 10.0

    def test_vmf_concentration_opposing_vectors(self):
        """Opposing/dispersed vectors sum to zero resultant, yielding kappa = 0."""
        vectors = np.array([[1.0, 0.0], [-1.0, 0.0]])
        kappa = vmf_concentration(vectors)
        assert kappa == pytest.approx(0.0, abs=1e-9)

    def test_vmf_concentration_unnormalized_rows(self):
        """Unnormalized input rows should be normalized automatically."""
        vectors = np.array([[5.0, 0.0], [10.0, 0.0]])
        kappa = vmf_concentration(vectors)
        assert kappa > 10.0

    def test_vmf_concentration_zero_vectors(self):
        """Zero vectors should be handled safely with epsilon fallback."""
        vectors = np.array([[0.0, 0.0], [0.0, 0.0]])
        kappa = vmf_concentration(vectors)
        assert kappa == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.parametrize(
        "invalid_shape_array",
        [
            np.array([]),
            np.array([1.0, 2.0, 3.0]),  # 1D
            np.zeros((0, 3)),  # 0 rows
            np.zeros((2, 2, 2)),  # 3D
        ],
    )
    def test_vmf_concentration_invalid_inputs(self, invalid_shape_array: np.ndarray):
        with pytest.raises(
            ValueError, match=r"vmf_concentration: expected a non-empty \(n, p\) array"
        ):
            vmf_concentration(invalid_shape_array)


class TestEpistemicState:
    """Test suite for EpistemicState derivation."""

    def test_derive_high_certainty_and_alignment(self):
        """Certain probability distribution + aligned embeddings => high rightness, low conflict."""
        probs = [1.0, 0.0]
        embeddings = np.array([[1.0, 0.0], [1.0, 0.0]])
        state = EpistemicState.derive(
            candidate_probabilities=probs,
            candidate_embeddings=embeddings,
            max_expected_entropy_bits=2.0,
        )

        assert state.shannon_entropy_bits == pytest.approx(0.0, abs=1e-9)
        assert state.dcu_kappa > 10.0
        assert state.feeling_of_rightness > 0.5
        assert state.feeling_of_error < 0.5
        assert state.feeling_of_conflict == pytest.approx(0.0, abs=1e-9)

    def test_derive_high_uncertainty_and_dispersed(self):
        """Uniform probability distribution + opposing embeddings => low rightness, high conflict."""
        probs = [0.25, 0.25, 0.25, 0.25]
        embeddings = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
        state = EpistemicState.derive(
            candidate_probabilities=probs,
            candidate_embeddings=embeddings,
            max_expected_entropy_bits=2.0,
        )

        assert state.shannon_entropy_bits == pytest.approx(2.0, abs=1e-6)
        assert state.dcu_kappa == pytest.approx(0.0, abs=1e-9)
        assert state.feeling_of_rightness == pytest.approx(0.0, abs=1e-9)
        assert state.feeling_of_error == pytest.approx(1.0, abs=1e-9)
        assert state.feeling_of_conflict == pytest.approx(1.0, abs=1e-6)

    def test_derive_max_expected_entropy_zero_boundary(self):
        """Zero or negative max_expected_entropy_bits should not cause division by zero."""
        probs = [0.5, 0.5]
        embeddings = np.array([[1.0, 0.0], [1.0, 0.0]])
        state = EpistemicState.derive(
            candidate_probabilities=probs,
            candidate_embeddings=embeddings,
            max_expected_entropy_bits=0.0,
        )
        assert isinstance(state, EpistemicState)
        assert state.shannon_entropy_bits == pytest.approx(1.0, abs=1e-6)
