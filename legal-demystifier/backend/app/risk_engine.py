import re

RISK_KEYWORDS = {
    "high": [r"penalt(?:y|ies)", r"indemnif", r"liabilit", r"arbitration", r"waiv", r"class action waiver"],
    "medium": [r"early termination fee", r"renewal", r"auto-?renew", r"late fee", r"governing law"],
}


def rule_score_for_clause(text: str) -> float:
    score = 0.0
    t = text.lower()
    for kw in RISK_KEYWORDS["high"]:
        if re.search(kw, t):
            score += 40
    for kw in RISK_KEYWORDS["medium"]:
        if re.search(kw, t):
            score += 15
    return min(100.0, score)


def combined_score(llm_score: float, rule_score: float, w_llm: float = 0.6) -> float:
    """
    Combine LLM-provided risk score with rule-based score.
    Expect both scores in 0-100 range.
    """
    return float(max(0.0, min(100.0, w_llm * llm_score + (1 - w_llm) * rule_score)))
