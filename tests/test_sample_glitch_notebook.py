import json
from pathlib import Path


NOTEBOOK = Path(__file__).parents[1] / "Test_Case" / "Sample_glitchBayesian.ipynb"


def _code_cells():
    notebook = json.loads(NOTEBOOK.read_text())
    return [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    ]


def test_every_sampler_cell_defines_max_calls_before_use():
    sampler_cells = [cell for cell in _code_cells() if "sampler.run(" in cell]

    assert sampler_cells
    for cell in sampler_cells:
        assert cell.index("max_calls =") < cell.index("max_ncalls= max_calls")


def test_notebook_does_not_compute_log_likelihood_via_exp():
    notebook_code = "\n".join(_code_cells())

    assert "np.log(1/" not in notebook_code
    assert "prob = -1e101" not in notebook_code
