from demand.scientist.evidence import Evidence


def confidence_from_evidence(evidence):

    if not evidence:
        return 0.0

    score = 0.0

    for e in evidence:

        if e.supported:
            score += e.effect_size

    return min(score / len(evidence), 1.0)
