from pathlib import Path

import pandas as pd

from openclaw_a_share_research_lab.educational_model import (
    DEFAULT_WEIGHTS,
    rank_candidates,
    score_frame,
)


def test_score_frame_applies_public_weights_with_lower_volatility_better():
    frame = pd.DataFrame(
        [
            {
                "code": "MOCK_A",
                "name": "A",
                "momentum_20d": 0.09,
                "reversal_5d": 0.01,
                "value_ep": 0.08,
                "turnover_stability": 0.7,
                "volatility_20d": 0.18,
            },
            {
                "code": "MOCK_B",
                "name": "B",
                "momentum_20d": 0.02,
                "reversal_5d": 0.04,
                "value_ep": 0.04,
                "turnover_stability": 0.4,
                "volatility_20d": 0.36,
            },
            {
                "code": "MOCK_C",
                "name": "C",
                "momentum_20d": 0.05,
                "reversal_5d": 0.03,
                "value_ep": 0.06,
                "turnover_stability": 0.6,
                "volatility_20d": 0.20,
            },
        ]
    )

    scored = score_frame(frame, weights=DEFAULT_WEIGHTS)

    assert list(scored.sort_values("educational_score", ascending=False)["code"])[0] == "MOCK_A"
    assert "educational_score" in scored.columns


def test_rank_candidates_returns_ranked_top_n(tmp_path):
    input_path = tmp_path / "features.csv"
    output_path = tmp_path / "top.json"
    pd.DataFrame(
        [
            {"code": "MOCK001", "name": "One", "momentum_20d": 0.08, "reversal_5d": 0.02, "value_ep": 0.06, "turnover_stability": 0.7, "volatility_20d": 0.22},
            {"code": "MOCK002", "name": "Two", "momentum_20d": 0.03, "reversal_5d": 0.05, "value_ep": 0.04, "turnover_stability": 0.5, "volatility_20d": 0.30},
            {"code": "MOCK003", "name": "Three", "momentum_20d": 0.06, "reversal_5d": 0.03, "value_ep": 0.05, "turnover_stability": 0.6, "volatility_20d": 0.25},
        ]
    ).to_csv(input_path, index=False)

    result = rank_candidates(input_path, output_path, top=2)

    assert len(result["top"]) == 2
    assert result["top"][0]["rank"] == 1
    assert output_path.exists()
