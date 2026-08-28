import warnings

import numpy as np
import pytest

from InferenceWorkflow.Likelihood import gaussian_log_likelihood


def test_gaussian_log_likelihood_matches_analytic_result():
    model = np.array([1.0, 4.0])
    observed = np.array([2.0, 2.0])
    uncertainty = np.array([0.5, 2.0])

    expected = np.sum(
        -0.5
        * (
            ((model - observed) / uncertainty) ** 2
            + np.log(2 * np.pi * uncertainty**2)
        )
    )

    assert gaussian_log_likelihood(model, observed, uncertainty) == pytest.approx(
        expected
    )


def test_gaussian_log_likelihood_does_not_underflow_for_poor_fit():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        result = gaussian_log_likelihood([1e6], [0.0], [1.0])

    assert np.isfinite(result)
    assert result < -1e11


def test_gaussian_log_likelihood_rejects_nonpositive_uncertainty():
    with pytest.raises(ValueError, match="must all be positive"):
        gaussian_log_likelihood([1.0], [1.0], [0.0])
