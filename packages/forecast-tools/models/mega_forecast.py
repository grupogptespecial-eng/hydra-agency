"""Simplified mega_forecast pipeline.

This module exposes ``mega_forecast`` which runs a tiny forecasting
pipeline used by the analyst worker.  The real project expects a richer
set of models and diagnostics; here we implement a minimal yet functional
version that follows the public design doc.  It performs:

* basic hygiene on the input DataFrame
* automatic splitting into correlation/train/test windows
* simple diagnostics (ADF, KPSS, seasonality strength, Granger p‑values)
* model selection between Naive, SeasonalNaive and ARIMA using Optuna
* evaluation on the test window with common metrics

The function returns a JSON‑serialisable dictionary containing the most
relevant pieces of information (diagnostics, leaderboard, champion model
and metrics).  The implementation favours clarity and keeps external
dependencies light so it can run inside the test suite quickly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import optuna
import pandas as pd
from optuna.samplers import TPESampler
from pandas import DataFrame, Series
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import acf, adfuller, grangercausalitytests, kpss
from statsmodels.tsa.statespace.sarimax import SARIMAX


# ---------------------------------------------------------------------------
# small metrics helpers
# ---------------------------------------------------------------------------

def smape(y_true: Series, y_pred: Series) -> float:
    denom = (np.abs(y_true) + np.abs(y_pred)).replace(0, np.finfo(float).eps)
    return float((2.0 * np.abs(y_true - y_pred) / denom).mean())


def mae(y_true: Series, y_pred: Series) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: Series, y_pred: Series) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mase(insample: Series, y_true: Series, y_pred: Series) -> float:
    naive = np.abs(np.diff(insample)).mean()
    if naive == 0:
        return float("nan")
    return float(mae(y_true, y_pred) / naive)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _default_splits(n: int) -> Dict[str, slice]:
    """Return default windows: 20% corr, 60% train, 20% test."""
    a = int(n * 0.2)
    b = int(n * 0.6)
    return {
        "corr": slice(0, a),
        "train": slice(a, a + b),
        "test": slice(a + b, n),
    }


@dataclass
class Diagnostics:
    adf_pvalue: float
    kpss_pvalue: float
    seasonality_m: int
    seasonality_strength: float
    granger_pvalues: Dict[str, float]


# ---------------------------------------------------------------------------
# main pipeline
# ---------------------------------------------------------------------------


def mega_forecast(
    df: DataFrame,
    target: str,
    alpha: float = 0.05,
    horizon: int = 21,
    splits: Optional[Dict[str, float]] = None,
    max_lag: int = 30,
    n_trials: int = 10,
    seed: int = 42,
    models_whitelist: Optional[List[str]] = None,
) -> Dict[str, any]:
    """Run the simplified mega forecast pipeline.

    Parameters
    ----------
    df : DataFrame
        Time indexed data containing the target and optional regressors.
    target : str
        Name of the target column.
    alpha : float, optional
        Significance level for intervals (unused in simplified version).
    horizon : int, optional
        Forecast horizon (number of steps into the future).
    splits : dict, optional
        Ratio for ``{"corr": x, "train": y, "test": z}``.
    max_lag : int, optional
        Maximum lag to evaluate Granger causality.
    n_trials : int, optional
        Number of Optuna trials per model.
    seed : int, optional
        Random seed.
    models_whitelist : list[str], optional
        Restrict the candidate model set.
    """

    if target not in df.columns:
        raise KeyError(f"target '{target}' not in DataFrame")

    df = df.sort_index().dropna()
    if len(df) < 10:
        raise ValueError("dataset too small")

    # resolve splits
    if splits is None:
        window = _default_splits(len(df))
    else:
        # assume ratios summing to 1
        n = len(df)
        a = int(n * splits.get("corr", 0.2))
        b = int(n * splits.get("train", 0.6))
        window = {
            "corr": slice(0, a),
            "train": slice(a, a + b),
            "test": slice(a + b, n),
        }

    y_corr = df[target].iloc[window["corr"]]
    X_corr = df.drop(columns=[target]).iloc[window["corr"]]
    y_train = df[target].iloc[window["train"]]
    X_train = df.drop(columns=[target]).iloc[window["train"]]
    y_test = df[target].iloc[window["test"]]
    X_test = df.drop(columns=[target]).iloc[window["test"]]

    # diagnostics -----------------------------------------------------------
    diag = {}
    diag["adf_pvalue"] = adfuller(y_train, autolag="AIC")[1]
    try:
        diag["kpss_pvalue"] = kpss(y_train, nlags="auto")[1]
    except Exception:
        diag["kpss_pvalue"] = float("nan")

    acfs = acf(y_train, nlags=min(30, len(y_train) // 2), fft=True)
    m = int(np.argmax(acfs[1:]) + 1) if len(acfs) > 1 else 0
    strength = 0.0
    if m > 1:
        try:
            stl = STL(y_train, period=m, robust=True).fit()
            strength = 1 - stl.resid.var() / (stl.seasonal.var() + stl.resid.var())
        except Exception:
            m = 0
            strength = 0.0
    diag["seasonality"] = {"m": m, "strength": strength, "strong": strength > 0.5}

    granger: Dict[str, float] = {}
    for col in X_corr.columns:
        try:
            tests = grangercausalitytests(pd.concat([y_corr, X_corr[col]], axis=1), maxlag=max_lag, verbose=False)
            pvals = [tests[i + 1][0]["ssr_ftest"][1] for i in range(max_lag)]
            granger[col] = float(min(pvals))
        except Exception:
            granger[col] = float("nan")
    diag["granger_pvalues"] = granger

    exog_selected = [c for c, p in granger.items() if not np.isnan(p) and p < alpha]

    # model selection ------------------------------------------------------
    candidates = ["naive"]
    if diag["seasonality"]["m"] > 1:
        candidates.append("snaive")
    candidates.append("arima")
    if models_whitelist:
        candidates = [c for c in candidates if c in models_whitelist]

    leaderboard: List[Dict[str, any]] = []
    tscv = TimeSeriesSplit(n_splits=3)

    for model_name in candidates:
        best_val = np.inf
        best_params: Dict[str, any] = {}

        if model_name == "naive":
            pred = y_train.shift(1).dropna()
            score = smape(y_train.loc[pred.index], pred)
            best_val = score
        elif model_name == "snaive":
            m = max(1, diag["seasonality"]["m"])
            pred = y_train.shift(m)
            pred = pred.dropna()
            score = smape(y_train.loc[pred.index], pred)
            best_val = score
        else:  # arima
            def objective(trial: optuna.Trial) -> float:
                p = trial.suggest_int("p", 0, 2)
                d = trial.suggest_int("d", 0, 1)
                q = trial.suggest_int("q", 0, 2)
                P = trial.suggest_int("P", 0, 1)
                D = trial.suggest_int("D", 0, 1)
                Q = trial.suggest_int("Q", 0, 1)
                m = diag["seasonality"]["m"]
                scores = []
                for train_idx, val_idx in tscv.split(y_train):
                    y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
                    if exog_selected:
                        X_tr = X_train.iloc[train_idx][exog_selected]
                        X_val = X_train.iloc[val_idx][exog_selected]
                    else:
                        X_tr = X_val = None
                    model = SARIMAX(y_tr, order=(p, d, q), seasonal_order=(P, D, Q, m), exog=X_tr, enforce_stationarity=False, enforce_invertibility=False)
                    res = model.fit(disp=False)
                    fc = res.forecast(steps=len(y_val), exog=X_val)
                    scores.append(smape(y_val, fc))
                return float(np.mean(scores))

            study = optuna.create_study(direction="minimize", sampler=TPESampler(seed=seed))
            study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
            best_val = study.best_value
            best_params = study.best_params

        leaderboard.append({"model": model_name, "best_params": best_params, "cv_score_smape": best_val})

    champion = sorted(leaderboard, key=lambda x: x["cv_score_smape"])[0]

    # fit champion on full train and forecast on test
    model_name = champion["model"]
    if model_name == "naive":
        yhat = pd.Series(y_train.iloc[-1], index=y_test.index)
    elif model_name == "snaive":
        m = max(1, diag["seasonality"]["m"])
        yhat = y_train.iloc[-m: ].reset_index(drop=True)
        yhat.index = y_test.index[: len(yhat)]
        if len(yhat) < len(y_test):
            yhat = yhat.reindex(y_test.index, method="ffill")
    else:
        params = champion["best_params"]
        m = diag["seasonality"]["m"]
        exog_train = X_train[exog_selected] if exog_selected else None
        exog_test = X_test[exog_selected] if exog_selected else None
        model = SARIMAX(y_train, order=(params.get("p",0), params.get("d",0), params.get("q",0)),
                        seasonal_order=(params.get("P",0), params.get("D",0), params.get("Q",0), m),
                        exog=exog_train, enforce_stationarity=False, enforce_invertibility=False)
        res = model.fit(disp=False)
        yhat = res.forecast(steps=len(y_test), exog=exog_test)

    metrics_test = {
        "smape": smape(y_test, yhat),
        "mae": mae(y_test, yhat),
        "rmse": rmse(y_test, yhat),
        "mase": mase(y_train, y_test, yhat),
    }

    out = {
        "meta": {
            "target": target,
            "alpha": alpha,
            "horizon": horizon,
            "splits": {
                k: (df.index[v.start], df.index[v.stop - 1]) if isinstance(v, slice) else v
                for k, v in window.items()
            },
            "seed": seed,
            "version": "mega-forecast-0.1",
        },
        "diagnostics": diag,
        "leaderboard": leaderboard,
        "champion": {"model": champion["model"], "params": champion["best_params"]},
        "metrics": {"test": metrics_test},
        "predictions": {
            "point": yhat.to_dict(),
        },
    }
    return out

__all__ = ["mega_forecast"]
