"""3D implied-volatility surface for BTC options using Deribit data."""

from __future__ import annotations

from datetime import datetime, timezone
from math import erf, log, sqrt

import certifi
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

DERIBIT_API = "https://www.deribit.com/api/v2"
HTTP_TIMEOUT = 10
DELTA_LIMIT = 0.5  # plot only OTM options (|delta| <= 0.5)
MIN_TTE_DAYS = 7  # keep weeklies for short-term context; drop sub-week dailies
MAX_TTE_DAYS = 365  # cap at ~1Y — covers all liquid Deribit expiries
MIN_MARK_PRICE_BTC = 0.0005  # ~$40 floor — sub-$40 options have unreliable mark_iv
MIN_MARK_IV = 0.20  # absolute lower bound — BTC realized vol rarely below 20%
MAX_MARK_IV = 1.20  # absolute upper bound — anything >120% is stale/junk
IV_OUTLIER_RATIO = 1.5  # per-expiry relative cap: drop quotes > ratio * expiry median


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _bs_delta(spot: float, strike: float, tte_years: float, sigma: float, is_call: bool) -> float | None:
    if tte_years <= 0 or sigma <= 0 or strike <= 0:
        return None
    d1 = (log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt(tte_years))
    call_delta = _norm_cdf(d1)
    return call_delta if is_call else call_delta - 1.0


def _get(path: str, params: dict) -> dict:
    resp = requests.get(
        f"{DERIBIT_API}{path}",
        params=params,
        timeout=HTTP_TIMEOUT,
        verify=certifi.where(),
    )
    resp.raise_for_status()
    return resp.json()["result"]


def _fetch_spot() -> float:
    return float(_get("/public/get_index_price", {"index_name": "btc_usd"})["index_price"])


def _fetch_option_summaries() -> list[dict]:
    return _get("/public/get_book_summary_by_currency", {"currency": "BTC", "kind": "option"})


def _build_dataframe(summaries: list[dict], spot: float) -> pd.DataFrame:
    df = pd.DataFrame(summaries)
    parts = df["instrument_name"].str.split("-", expand=True)
    df["expiry"] = pd.to_datetime(parts[1], format="%d%b%y", utc=True) + pd.Timedelta(hours=8)
    df["strike"] = parts[2].astype(float)
    df["option_type"] = parts[3]

    now = pd.Timestamp.now(tz="UTC")
    df["tte_years"] = (df["expiry"] - now).dt.total_seconds() / (365.25 * 24 * 3600)

    df["mark_iv"] = pd.to_numeric(df["mark_iv"], errors="coerce") / 100.0
    df["mark_price"] = pd.to_numeric(df["mark_price"], errors="coerce")
    df = df.dropna(subset=["mark_iv", "mark_price"])
    df = df[
        (df["mark_iv"] >= MIN_MARK_IV)
        & (df["mark_iv"] <= MAX_MARK_IV)
        & (df["tte_years"] >= MIN_TTE_DAYS / 365.25)
        & (df["tte_years"] <= MAX_TTE_DAYS / 365.25)
        & (df["mark_price"] >= MIN_MARK_PRICE_BTC)
    ].copy()
    expiry_median_iv = df.groupby("expiry")["mark_iv"].transform("median")
    df = df[df["mark_iv"] <= IV_OUTLIER_RATIO * expiry_median_iv]

    df["delta"] = df.apply(
        lambda r: _bs_delta(spot, r["strike"], r["tte_years"], r["mark_iv"], r["option_type"] == "C"),
        axis=1,
    )
    df = df.dropna(subset=["delta"])
    df = df[df["delta"].abs() <= DELTA_LIMIT]

    return df[["expiry", "tte_years", "delta", "mark_iv", "option_type"]].reset_index(drop=True)


def _plot_surface(grid: pd.DataFrame, spot: float) -> None:
    if len(grid) < 4:
        raise RuntimeError(f"Not enough option data to render a surface (got {len(grid)} points)")

    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_subplot(projection="3d")
    surf = ax.plot_trisurf(
        grid["delta"].to_numpy(),
        grid["tte_years"].to_numpy(),
        grid["mark_iv"].to_numpy(),
        cmap="viridis",
        edgecolor="none",
        alpha=0.9,
    )
    fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.15, label="Implied volatility")

    ax.set_xlabel("Delta", fontsize=9)
    ax.set_ylabel("Expiry", fontsize=9)
    ax.set_zlabel("Implied volatility", fontsize=9)
    ax.tick_params(axis="x", labelsize=7)
    ax.tick_params(axis="y", labelsize=7)
    ax.tick_params(axis="z", labelsize=7)
    ax.set_xlim(-DELTA_LIMIT, DELTA_LIMIT)
    ax.set_xticks([-0.4, -0.2, 0.0, 0.2, 0.4])
    ax.set_xticklabels(["40p", "20p", "ATM", "20c", "40c"])

    expiries = (
        grid[["expiry", "tte_years"]]
        .drop_duplicates()
        .sort_values("tte_years")
        .reset_index(drop=True)
    )
    n_ticks = min(7, len(expiries))
    targets = np.linspace(expiries["tte_years"].iloc[0], expiries["tte_years"].iloc[-1], n_ticks)
    picked = []
    for t in targets:
        idx = (expiries["tte_years"] - t).abs().idxmin()
        if idx not in picked:
            picked.append(idx)
    expiries = expiries.loc[picked]
    ax.set_yticks(expiries["tte_years"].to_numpy())
    ax.set_yticklabels([d.strftime("%d %b %y") for d in expiries["expiry"]])

    ax.view_init(elev=22, azim=-55)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ax.set_title(f"BTC IV surface — spot ${spot:,.0f} — {ts}")

    plt.tight_layout()
    plt.show()


def run() -> None:
    print("Fetching BTC spot from Deribit...")
    spot = _fetch_spot()
    print(f"Spot: ${spot:,.2f}")

    print("Fetching BTC option book summaries...")
    summaries = _fetch_option_summaries()
    print(f"Received {len(summaries)} instruments")

    grid = _build_dataframe(summaries, spot)
    print(f"Plotting surface with {len(grid)} (delta, expiry) points across {grid['expiry'].nunique()} expiries")

    _plot_surface(grid, spot)
