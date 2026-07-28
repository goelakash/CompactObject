import os
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

import InferenceWorkflow.Likelihood as likelihood
from InferenceWorkflow.DDH_Likelihood import Likelihood as DDHLikelihood


class DDHLikelihoodPathTests(unittest.TestCase):
    def test_crust_file_loads_from_test_case_cwd(self):
        old_cwd = Path.cwd()
        try:
            os.chdir(old_cwd / "Test_Case")
            DDHLikelihood.eps_com = None
            DDHLikelihood.pres_com = None
            DDHLikelihood.initialize_crust_data()
            self.assertIsNotNone(DDHLikelihood.eps_com)
            self.assertIsNotNone(DDHLikelihood.pres_com)
            self.assertGreater(DDHLikelihood.eps_com.size, 0)
            self.assertEqual(DDHLikelihood.eps_com.size, DDHLikelihood.pres_com.size)
        finally:
            os.chdir(old_cwd)

    def test_chieft_super_gaussian_uses_numpy2_compatible_inf(self):
        eos_pnm = np.array(
            [
                [0.08, 0.12, 0.16],
                [8.0, 12.0, 16.0],
                [0.5, 1.2, 2.5],
            ]
        )

        value = likelihood.chiEFT_PNM(
            eos_pnm,
            type="Super Gaussian",
            contraint_quantity="p",
            enlargement=1.0,
        )

        self.assertTrue(np.isfinite(value))

    def test_pqcd_likelihood_is_deterministic(self):
        eos = np.array(
            [
                [0.5, 1.5],
                [0.2, 0.8],
                [0.1, 0.4],
            ]
        )

        with patch(
            "InferenceWorkflow.Likelihood.constraints",
            side_effect=lambda scale, energy, pressure, rho: scale < 2.0,
        ):
            first = likelihood.ln_pQCD(eos, rho_list=[1.0], points=1000)
            second = likelihood.ln_pQCD(eos, rho_list=[1.0], points=1000)

        self.assertEqual(first, second)
        self.assertAlmostEqual(first, np.log(0.5))

    def test_pqcd_likelihood_rejects_invalid_point_count(self):
        eos = np.ones((3, 2))

        with self.assertRaisesRegex(ValueError, "positive integer"):
            likelihood.ln_pQCD(eos, points=0)


if __name__ == "__main__":
    unittest.main()
