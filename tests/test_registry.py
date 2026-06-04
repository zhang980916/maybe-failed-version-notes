from pathlib import Path

from openclaw_a_share_research_lab.gladiator import score_combinations
from openclaw_a_share_research_lab.registry import read_factors_csv, summarize_factor_categories


ROOT = Path(__file__).resolve().parents[1]
FACTORS = ROOT / "examples" / "mock_data" / "factors.csv"


def test_factor_category_summary_counts_active_only():
    factors = read_factors_csv(FACTORS)
    summary = summarize_factor_categories(factors)

    assert summary["momentum"] == 2
    assert summary["risk"] == 1
    assert "deprecated" not in summary


def test_gladiator_scores_mock_combinations():
    rankings = score_combinations(FACTORS, max_size=2)

    assert rankings
    assert rankings[0].robustness_score >= rankings[-1].robustness_score
