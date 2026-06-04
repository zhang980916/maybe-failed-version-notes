from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main() -> None:
    run([
        "-m",
        "openclaw_a_share_research_lab.registry",
        "build",
        "--factors",
        "examples/mock_data/factors.csv",
        "--out",
        "data/factor_registry.json",
    ])
    run([
        "-m",
        "openclaw_a_share_research_lab.registry",
        "log-experiment",
        "--manifest",
        "examples/mock_data/experiment_manifest.json",
        "--out",
        "data/experiments.jsonl",
    ])
    run([
        "-m",
        "openclaw_a_share_research_lab.gladiator",
        "--factors",
        "examples/mock_data/factors.csv",
        "--out",
        "data/gladiator_rankings.json",
    ])
    run([
        "-m",
        "openclaw_a_share_research_lab.dashboard_bridge",
        "--mock-dir",
        "examples/mock_data",
        "--out",
        "dashboard/dashboard_data.json",
    ])


if __name__ == "__main__":
    main()
