from dataclasses import dataclass
from statistics import mean


@dataclass(slots=True)
class ValidationResult:
    state: str
    observations: int
    lead_days: int
    correlation: float
    accepted: bool


def pearson(x: list[float], y: list[float]) -> float:

    mx = mean(x)
    my = mean(y)

    cov = sum((a-mx)*(b-my) for a,b in zip(x,y))

    vx = sum((a-mx)**2 for a in x)
    vy = sum((b-my)**2 for b in y)

    if vx == 0 or vy == 0:
        return 0.0

    return cov / ((vx*vy) ** 0.5)


def validate_state(
    state: str,
    signals: list[float],
    outcomes: list[float],
    max_lead: int = 30,
) -> ValidationResult:

    best_corr = -1.0
    best_lead = 0

    for lead in range(max_lead + 1):

        xs = signals[:-lead] if lead else signals
        ys = outcomes[lead:] if lead else outcomes

        if len(xs) < 5:
            continue

        corr = pearson(xs, ys)

        if abs(corr) > abs(best_corr):
            best_corr = corr
            best_lead = lead

    return ValidationResult(
        state=state,
        observations=len(signals),
        lead_days=best_lead,
        correlation=best_corr,
        accepted=abs(best_corr) > 0.50,
    )
