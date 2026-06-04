from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

from .paths import ensure_parent
from .registry import read_factors_csv, utc_now


@dataclass(frozen=True)
class ComboScore:
    combo_id: str
    factors: tuple[str, ...]
    category_count: int
    mean_ic_20d: float
    robustness_score: float


def score_combinations(factors_path: Path, max_size: int = 3) -> list[ComboScore]:
    factors = [factor for factor in read_factors_csv(factors_path) if factor.status == "active"]
    rows: list[ComboScore] = []
    for size in range(2, max_size + 1):
        for combo in itertools.combinations(factors, size):
            names = tuple(factor.name for factor in combo)
            categories = {factor.category for factor in combo}
            ic_values = [factor.last_ic_20d or 0.0 for factor in combo]
            mean_ic = sum(ic_values) / len(ic_values)
            diversity_bonus = min(len(categories) * 0.01, 0.03)
            concentration_penalty = 0.01 if len(categories) == 1 else 0.0
            score = mean_ic + diversity_bonus - concentration_penalty
            rows.append(
                ComboScore(
                    combo_id="-".join(sorted(names))[:80],
                    factors=names,
                    category_count=len(categories),
                    mean_ic_20d=round(mean_ic, 5),
                    robustness_score=round(score, 5),
                )
            )
    return sorted(rows, key=lambda row: row.robustness_score, reverse=True)


def write_rankings(rankings: list[ComboScore], out_path: Path) -> None:
    ensure_parent(out_path)
    payload = {
        "schema": "gladiator_rankings.v1",
        "generated_at": utc_now(),
        "note": "Synthetic demo ranking. Do not treat as a trading signal.",
        "rankings": [
            {
                "rank": index + 1,
                "combo_id": row.combo_id,
                "factors": list(row.factors),
                "category_count": row.category_count,
                "mean_ic_20d": row.mean_ic_20d,
                "robustness_score": row.robustness_score,
            }
            for index, row in enumerate(rankings)
        ],
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small synthetic factor-combo arena")
    parser.add_argument("--factors", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-size", type=int, default=3)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    rankings = score_combinations(args.factors, max_size=args.max_size)[: args.top]
    write_rankings(rankings, args.out)
    print(json.dumps({"written": str(args.out), "rows": len(rankings)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
