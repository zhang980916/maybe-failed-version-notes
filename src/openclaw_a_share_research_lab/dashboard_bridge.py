from __future__ import annotations

import argparse
import json
from pathlib import Path

from .paths import ensure_parent
from .registry import read_experiments, read_factors_csv, summarize_factor_categories, utc_now


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_dashboard_data(mock_dir: Path) -> dict:
    factors_path = mock_dir / "factors.csv"
    experiments_path = mock_dir / "experiments.jsonl"
    candidates_path = mock_dir / "candidates.json"

    factors = read_factors_csv(factors_path)
    experiments = read_experiments(experiments_path)
    candidates = load_json(candidates_path, {"top5": []})

    return {
        "schema": "signal_dashboard.v1",
        "generated_at": utc_now(),
        "mode": "mock",
        "summary": {
            "active_factor_count": sum(1 for factor in factors if factor.status == "active"),
            "factor_categories": summarize_factor_categories(factors),
            "experiment_count": len(experiments),
            "top_candidate_count": len(candidates.get("top5", [])),
        },
        "top5": candidates.get("top5", []),
        "recent_experiments": experiments[-5:],
        "disclaimer": "Synthetic demo data only. Not investment advice.",
    }


def write_dashboard_data(payload: dict, out_path: Path) -> None:
    ensure_parent(out_path)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dashboard JSON from mock research artifacts")
    parser.add_argument("--mock-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    payload = build_dashboard_data(args.mock_dir)
    write_dashboard_data(payload, args.out)
    print(json.dumps({"written": str(args.out), "mode": payload["mode"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
