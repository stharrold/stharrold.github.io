"""Every stage of the runner end to end on a small synthetic snapshot, in quick mode (not the registered settings)."""

import json

import pytest

from ratchet import run, synthetic

STAGES = {
    "enrollment": ["groups", "phase_in"],
    "validate": ["passed", "sigma_v_model", "step1"],
    "power": ["h1", "h2", "h3"],
    "confirm": ["groups", "h3", "imputed_by_group"],
    "robustness": [f"{i}_" for i in range(1, 10)],
    "exploratory": [
        "census_region_in_h3",
        "leavers",
        "enhanced_early_renewers",
        "pull_times_w",
        "capped_regional_component",
        "who_renewed",
        "balance",
        "spending_by_agreement_year",
    ],
}


@pytest.fixture(scope="module")
def outputs(tmp_path_factory):
    data = tmp_path_factory.mktemp("data")
    out = tmp_path_factory.mktemp("out")
    synthetic.generate(data, seed=12, n_base=(80, 60), n_validation=40, hist_noise=0.02, by_noise=0.02)
    for stage in STAGES:
        run.main([stage, "--data-dir", str(data), "--out-dir", str(out), "--quick", "--workers", "2"])
    return out


@pytest.mark.parametrize("stage", list(STAGES))
def test_stage_writes_expected_keys(outputs, stage):
    name = "validation.json" if stage == "validate" else f"{stage}.json"
    payload = json.loads((outputs / name).read_text())
    assert payload["synthetic"] is True and payload["git_commit"]
    for key in STAGES[stage]:
        assert any(k.startswith(key) for k in payload), f"{stage}.json lacks {key}"
