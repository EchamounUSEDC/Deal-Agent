"""
utils/sample_data.py — deterministic 90-day demo dataset.

`seed_if_empty()` populates the calls table ONLY when it is empty, and
tags every row source='sample', so it can never overwrite real analyzed
calls. The generator is seeded, so every fresh install produces the same
data — demos and screenshots are reproducible.

The data has deliberate structure for the analytics tabs to find:
- each rep has a skill level (drives conversion rate and score),
- Tuesday/Thursday afternoons convert best,
- objection mix varies by rep (fuels per-rep coaching).
"""

from __future__ import annotations

import random
from datetime import datetime, time, timedelta

from utils.database import count_calls, insert_calls

_SEED = 42
_DAYS = 90

# (name, territory, skill 0-1, weakness objection bias)
REPS = [
    ("Priya Raman",   "Midwest",   0.72, "Fees feel high"),
    ("Marcus Bell",   "Northeast", 0.63, "Liquidity concerns"),
    ("Elena Torres",  "West",      0.58, "Market volatility"),
    ("Dana Whitfield", "Southeast", 0.54, "Needs spouse/advisor sign-off"),
    ("Jake Sullivan", "Southwest", 0.47, "Timing — next quarter"),
    ("Tom Okafor",    "Northeast", 0.43, "Fees feel high"),
]

PRODUCTS = [
    "Energy Income Fund",
    "Drilling Partnership",
    "1031 Exchange Program",
    "Royalty Program",
    "Opportunity Zone Fund",
]

OBJECTIONS = [
    "Fees feel high",
    "Market volatility",
    "Liquidity concerns",
    "Needs spouse/advisor sign-off",
    "Timing — next quarter",
    "Already invested elsewhere",
    "Risk tolerance",
]

# What a rep might actually say when a call goes sideways — grounding for
# the Sales Coach "said vs. try instead" rewrites.
WEAK_LINES = {
    "Fees feel high": "I know the fees look steep, but that's just how these funds work.",
    "Market volatility": "Yeah, the market's been crazy, there's not much anyone can do about that.",
    "Liquidity concerns": "It's locked up for a while, but most people don't mind.",
    "Needs spouse/advisor sign-off": "Okay, just call me back whenever you've talked to them.",
    "Timing — next quarter": "No problem, I'll try you again in a few months.",
    "Already invested elsewhere": "Oh, then this probably isn't for you.",
    "Risk tolerance": "It's oil and gas, so yeah, there's always some risk.",
}

STRONG_LINES = [
    "Walk me through what a win would look like for you twelve months from now.",
    "Most of my clients felt the same way until they saw the distribution history — can I share it?",
    "What would need to be true for this to be an easy yes?",
    "Let's put a 15-minute call on the calendar with your advisor on the line too.",
]

FIRST = ["Alex", "Sam", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Jamie",
         "Chris", "Pat", "Drew", "Robin", "Lee", "Quinn", "Avery", "Blake"]
LAST = ["Nguyen", "Garcia", "Smith", "Johnson", "Chen", "Patel", "Brown",
        "Davis", "Kim", "Lopez", "Miller", "Wilson", "Anderson", "Clark"]


def _conversion_prob(skill: float, dt: datetime) -> float:
    p = 0.10 + skill * 0.30
    if dt.weekday() in (1, 3) and 13 <= dt.hour <= 16:  # Tue/Thu afternoons
        p += 0.12
    if dt.weekday() == 4 and dt.hour >= 15:  # late Friday slump
        p -= 0.06
    return max(0.03, min(0.9, p))


def build_sample_calls(now: datetime | None = None) -> list[dict]:
    rng = random.Random(_SEED)
    now = now or datetime.now()
    start = (now - timedelta(days=_DAYS)).date()
    rows: list[dict] = []

    for day_offset in range(_DAYS):
        day = start + timedelta(days=day_offset)
        if day.weekday() >= 5:  # weekends off
            continue
        for name, territory, skill, weak_bias in REPS:
            for _ in range(rng.randint(1, 4)):
                dt = datetime.combine(
                    day, time(hour=rng.randint(9, 17), minute=rng.randrange(0, 60))
                )
                converted = rng.random() < _conversion_prob(skill, dt)
                outcome = (
                    "converted" if converted
                    else rng.choices(["follow_up", "no_sale"], weights=[55, 45])[0]
                )

                pool = OBJECTIONS + [weak_bias] * 3  # bias toward the rep's weakness
                n_obj = rng.choices([0, 1, 2, 3], weights=[15, 45, 30, 10])[0]
                objections = sorted(set(rng.sample(pool, k=n_obj + 2)[:n_obj])) if n_obj else []

                base = 38 + skill * 42 + rng.gauss(0, 9)
                base += {"converted": 12, "follow_up": 2, "no_sale": -8}[outcome]
                score = int(max(5, min(98, base)))

                if objections and score < 62:
                    snippet = WEAK_LINES[objections[0]] if objections[0] in WEAK_LINES \
                        else rng.choice(list(WEAK_LINES.values()))
                else:
                    snippet = rng.choice(STRONG_LINES)

                product = rng.choice(PRODUCTS)
                customer = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
                duration = round(max(4.0, rng.gauss(16 + skill * 10, 7)), 1)
                summary = (
                    f"{customer} asked about the {product}. "
                    + (f"Raised: {', '.join(objections)}. " if objections else "")
                    + {"converted": "Committed to move forward.",
                       "follow_up": "Agreed to a follow-up call.",
                       "no_sale": "Passed for now."}[outcome]
                )

                rows.append({
                    "call_time": dt.isoformat(sep=" ", timespec="seconds"),
                    "rep_name": name,
                    "territory": territory,
                    "customer_name": customer,
                    "duration_min": duration,
                    "product_interest": product,
                    "objections": objections,
                    "outcome": outcome,
                    "score": score,
                    "summary": summary,
                    "transcript_snippet": snippet,
                    "source": "sample",
                })
    return rows


def seed_if_empty() -> bool:
    """Seed demo data on first launch only. Returns True if it seeded."""
    if count_calls() > 0:
        return False
    insert_calls(build_sample_calls())
    return True
