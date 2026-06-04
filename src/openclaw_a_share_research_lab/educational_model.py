from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .paths import ensure_parent
from .registry import utc_now


DEFAULT_WEIGHTS: dict[str, float] = {
    "momentum_20d": 0.30,
    "reversal_5d": 0.20,
    "value_ep": 0.20,
    "turnover_stability": 0.15,
    "volatility_20d": -0.15,
}

REQUIRED_COLUMNS = {"code", "name", *DEFAULT_WEIGHTS.keys()}


def zscore(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    std = values.std(ddof=0)
    if pd.isna(std) or std == 0:
        return values.fillna(0.0) * 0.0
    return (values - values.mean()) / std


def score_frame(frame: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    weights = weights or DEFAULT_WEIGHTS
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    scored = frame.copy()
    score = pd.Series(0.0, index=scored.index)
    contributions: dict[str, pd.Series] = {}

    for factor_name, weight in weights.items():
        contribution = zscore(scored[factor_name]) * weight
        contributions[f"{factor_name}_contribution"] = contribution
        score = score + contribution

    for column, values in contributions.items():
        scored[column] = values.round(6)
    scored["educational_score"] = score.round(6)
    return scored


def rank_candidates(input_path: Path, output_path: Path | None = None, top: int = 5) -> dict:
    frame = pd.read_csv(input_path)
    scored = score_frame(frame)
    ranked = scored.sort_values("educational_score", ascending=False).head(top).reset_index(drop=True)

    top_rows = []
    for idx, row in ranked.iterrows():
        top_rows.append(
            {
                "rank": idx + 1,
                "code": str(row["code"]),
                "name": str(row["name"]),
                "educational_score": float(row["educational_score"]),
                "factors": {
                    factor_name: float(row[factor_name])
                    for factor_name in DEFAULT_WEIGHTS
                },
            }
        )

    payload = {
        "schema": "educational_factor_model.v1",
        "generated_at": utc_now(),
        "note": "Educational toy model using synthetic/demo inputs. Not investment advice.",
        "weights": DEFAULT_WEIGHTS,
        "top": top_rows,
    }

    if output_path:
        ensure_parent(output_path)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the educational factor model on a CSV feature matrix")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    payload = rank_candidates(args.input, args.out, top=args.top)
    print(json.dumps({"written": str(args.out), "rows": len(payload["top"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
