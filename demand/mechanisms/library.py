"""
Built-in library of reusable demand mechanisms.
"""

from __future__ import annotations

from .models import Mechanism


MECHANISMS = [

    Mechanism(
        name="Seasonality",
        trigger="Summer",
        human_change="People seek cooling",
        market_effect="Cooling-related demand increases",
    ),

    Mechanism(
        name="Scarcity",
        trigger="Limited Supply",
        human_change="Urgency increases",
        market_effect="Purchases accelerate",
    ),

    Mechanism(
        name="Major Sporting Event",
        trigger="International Sports",
        human_change="Fan engagement rises",
        market_effect="Sports-related demand increases",
    ),

    Mechanism(
        name="Technology Launch",
        trigger="Major Product Release",
        human_change="Public attention increases",
        market_effect="Technology ecosystem demand increases",
    ),

    Mechanism(
        name="Holiday",
        trigger="Public Holiday",
        human_change="People spend more leisure time",
        market_effect="Consumer demand shifts",
    ),

]


def all_mechanisms() -> list[Mechanism]:
    return list(MECHANISMS)
