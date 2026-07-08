"""Latest-vs-previous report summary: per-category rows plus header freshness fields."""

from __future__ import annotations

import pandas as pd

from cot.fields import CATEGORIES, LABELS, POSITION_FIELDS
from cot.values import opt_float, opt_int

PUBLICATION_LAG = pd.Timedelta(days=3)  # report Tuesday -> publication Friday
NEW_WINDOW = pd.Timedelta(days=4)
STALE_AFTER = pd.Timedelta(days=14)


def build(history: pd.DataFrame, index: pd.DataFrame, prices: pd.Series, now: pd.Timestamp) -> dict:
    last = history.iloc[-1]
    report_date = history.index[-1]
    publication = report_date + PUBLICATION_LAG
    price = opt_float(prices.iloc[-1])
    oi = float(last["oi"])

    rows = []
    for cat in CATEGORIES:
        net = float(last[f"{cat}_net"])
        delta = opt_float(last[f"{cat}_delta"])
        prev_net = net - delta if delta is not None else None
        rows.append(
            {
                "category": cat,
                "label": LABELS[cat],
                "long_btc": float(last[f"{cat}_long"]),
                "short_btc": float(last[f"{cat}_short"]),
                "spread_btc": float(last[f"{cat}_spread"]) if POSITION_FIELDS[cat]["spread"] else None,
                "net_btc": net,
                "delta_net_btc": delta,
                # % change is meaningless when the prior net sits at zero
                "delta_net_pct": (
                    delta / abs(prev_net) * 100.0
                    if delta is not None and prev_net is not None and abs(prev_net) >= 1.0
                    else None
                ),
                "net_pct_of_oi": net / oi * 100.0 if oi else None,
                "index": opt_float(index[cat].iloc[-1]),
                "traders_long": opt_int(last[f"traders_{cat}_long"]),
                "traders_short": opt_int(last[f"traders_{cat}_short"]),
            }
        )

    return {
        "report_date": report_date,
        "prev_report_date": history.index[-2] if len(history) > 1 else None,
        "publication_date": publication,
        "is_new": now - publication <= NEW_WINDOW,
        "is_stale": now - report_date > STALE_AFTER,
        "oi_btc": oi,
        "delta_oi_btc": opt_float(last["oi_delta"]),
        "btc_price": price,
        "oi_usd": oi * price if price is not None else None,
        "rows": rows,
    }
