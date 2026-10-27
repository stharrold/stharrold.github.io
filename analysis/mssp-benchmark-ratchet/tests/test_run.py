"""Runner guards: stage order, quick settings only on synthetic data, synthetic output kept out of results/."""

import pytest

from ratchet import config, run, synthetic


@pytest.fixture(scope="module")
def data_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("synthetic")
    synthetic.generate(d, seed=3, n_base=(60, 50), n_validation=30)
    return d


def test_confirm_refuses_before_validation(data_dir, tmp_path):
    with pytest.raises(SystemExit, match="validation.json is missing"):
        run.main(["confirm", "--data-dir", str(data_dir), "--out-dir", str(tmp_path), "--quick", "--workers", "1"])


def test_power_refuses_before_validation(data_dir, tmp_path):
    with pytest.raises(SystemExit, match="validation.json is missing"):
        run.main(["power", "--data-dir", str(data_dir), "--out-dir", str(tmp_path), "--quick", "--workers", "1"])


def test_synthetic_output_cannot_go_to_results(data_dir):
    with pytest.raises(SystemExit, match="must write elsewhere"):
        run.main(["validate", "--data-dir", str(data_dir), "--quick"])


@pytest.mark.skipif(not config.DEFAULT_DATA_DIR.exists(), reason="real snapshot not in cache")
def test_quick_refused_on_real_data(tmp_path):
    with pytest.raises(SystemExit, match="only for synthetic"):
        run.main(["enrollment", "--out-dir", str(tmp_path), "--quick"])


def test_validate_stage_writes_result(data_dir, tmp_path):
    run.main(["validate", "--data-dir", str(data_dir), "--out-dir", str(tmp_path), "--quick", "--workers", "1"])
    assert (tmp_path / "validation.json").exists()
