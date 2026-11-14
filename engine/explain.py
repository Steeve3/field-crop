"""Evidence Cards from templates (Dev A). An LLM may rewrite the text later, never the numbers.

Each card: why, 3–5 evidence items (claim + metric key + source + confidence), up to 3 benefits,
up to 3 risks, information gaps, needs local review, confidence.

Information gaps that are always true for this app (add them to every card):
- No on-farm soil test; soil effects are estimated from the crop sequence only.
- Weather is NASA POWER at ~50 km resolution, not a field weather station.
- Prices and costs are placeholders, not current market data.
- Pest and disease pressure is not observed.

Needs local review (always): variety choice, fertiliser rates, water rights / irrigation
availability, equipment fit, buyers and contracts.
"""
from __future__ import annotations

from .schema import EvidenceCard


def evidence_card(strategy: dict, s0: dict, climate: dict) -> EvidenceCard:
    raise NotImplementedError("Dev A: implement Evidence Cards")
