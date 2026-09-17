from dataclasses import dataclass


@dataclass(frozen=True)
class RiskSignal:
    """A deterministic risk signal detected by NeuroShield."""

    name: str
    category: str
    severity: str
    penalty: float
    description: str
    recommendation: str


class RiskEngine:
    """
    Deterministic risk scoring engine.

    The LLM identifies/explains information, while this engine
    converts validated signals into a reproducible score.
    """

    def calculate_score(
        self,
        signals: list[RiskSignal],
    ) -> float:
        score = 100.0

        for signal in signals:
            score -= signal.penalty

        return max(0.0, min(100.0, score))

    def verdict(self, score: float) -> str:
        if score >= 80:
            return "Safe"

        if score >= 50:
            return "Moderate Risk"

        if score >= 25:
            return "High Risk"

        return "Critical Risk"