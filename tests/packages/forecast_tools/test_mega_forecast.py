import importlib.util
import pathlib
import sys

import numpy as np
import pandas as pd

repo_root = pathlib.Path(__file__).resolve().parents[3]
sys.path.append(str(repo_root))

module_path = repo_root / "packages" / "forecast-tools" / "models" / "mega_forecast.py"
spec = importlib.util.spec_from_file_location("forecast_tools.models.mega_forecast", module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module  # needed for dataclasses decorator
spec.loader.exec_module(module)
mega_forecast = module.mega_forecast


def _make_series(n=120, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    seasonal = np.sin(2 * np.pi * np.arange(n) / 7)
    trend = np.linspace(0, 1, n)
    noise = rng.normal(scale=0.1, size=n)
    x = seasonal + trend + noise
    y = x + rng.normal(scale=0.1, size=n)
    df = pd.DataFrame({"y": y, "x": x}, index=idx)
    return df


def test_mega_forecast_basic():
    df = _make_series()
    result = mega_forecast(df, target="y", n_trials=3, seed=1)
    assert result["diagnostics"]["seasonality"]["strong"]
    assert result["champion"]["model"] in {"naive", "snaive", "arima"}
    assert "smape" in result["metrics"]["test"]
