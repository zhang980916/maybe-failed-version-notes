from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .paths import ensure_parent


@dataclass(frozen=True)
class Factor:
    factor_id: str
    name: str
    category: str
    definition: str
    window_days: int
    status: str = "active"
    source: str = "mock"
    last_ic_20d: float | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_factors_csv(path: Path) -> list[Factor]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        factors: list[Factor] = []
        for row in rows:
            factors.append(
                Factor(
                    factor_id=row["factor_id"],
                    name=row["name"],
                    category=row["category"],
                    definition=row["definition"],
                    window_days=int(row["window_days"]),
                    status=row.get("status") or "active",
                    source=row.get("source") or "mock",
                    last_ic_20d=float(row["last_ic_20d"]) if row.get("last_ic_20d") else None,
                )
            )
        return factors


def write_factor_registry(factors: Iterable[Factor], out_path: Path) -> None:
    ensure_parent(out_path)
    payload = {
        "schema": "factor_registry.v1",
        "generated_at": utc_now(),
        "factors": [asdict(factor) for factor in factors],
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_experiment(manifest_path: Path, out_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = {
        "schema": "experiment_record.v1",
        "experiment_id": f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "recorded_at": utc_now(),
        **manifest,
    }
    ensure_parent(out_path)
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def read_experiments(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def summarize_factor_categories(factors: Iterable[Factor]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for factor in factors:
        if factor.status != "active":
            continue
        summary[factor.category] = summary.get(factor.category, 0) + 1
    return dict(sorted(summary.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Research registry utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Build a JSON factor registry")
    build.add_argument("--factors", type=Path, required=True)
    build.add_argument("--out", type=Path, required=True)

    log = sub.add_parser("log-experiment", help="Append one experiment record")
    log.add_argument("--manifest", type=Path, required=True)
    log.add_argument("--out", type=Path, required=True)

    args = parser.parse_args()

    if args.command == "build":
        factors = read_factors_csv(args.factors)
        write_factor_registry(factors, args.out)
        print(json.dumps({"written": str(args.out), "categories": summarize_factor_categories(factors)}, ensure_ascii=False))
    elif args.command == "log-experiment":
        record = append_experiment(args.manifest, args.out)
        print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
