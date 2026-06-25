"""Smoke tests for the Go/No-Go engine — run with: python -m deal_agent.gonogo.tests.test_engine

No API key required; these exercise the deterministic layer only.
"""

from __future__ import annotations

from deal_agent.gonogo import DealMetrics, rank_deals, score_deal
from deal_agent.gonogo.benchmarks import BENCHMARKS


def _strong_like_hamburg() -> DealMetrics:
    h = BENCHMARKS["Hamburg"]
    return DealMetrics(
        name="Hamburg-like", yield_on_cost=h.yield_on_cost, exit_cap=h.exit_cap,
        dev_spread_bps=h.dev_spread_bps, levered_irr=h.levered_irr, moic=h.moic,
        lease_up_months=h.lease_up_months,
    )


def _weak_deal() -> DealMetrics:
    return DealMetrics(
        name="Weak", yield_on_cost=0.058, exit_cap=0.068, dev_spread_bps=-100,
        levered_irr=0.06, moic=1.2, lease_up_months=20,
    )


def test_benchmark_like_is_go():
    v = score_deal(_strong_like_hamburg())
    assert v.decision == "GO", v.rationale


def test_weak_is_no_go():
    v = score_deal(_weak_deal())
    assert v.decision == "NO-GO", v.rationale
    assert v.knockouts, "weak deal should trip at least one hard knockout"


def test_irr_knockout_overrides_strong_metrics():
    # Strong spread/YoC but IRR below the 10% floor -> still NO-GO.
    d = DealMetrics(name="IRR-fail", yield_on_cost=0.082, exit_cap=0.058,
                    dev_spread_bps=240, levered_irr=0.09, moic=1.5, lease_up_months=10)
    v = score_deal(d)
    assert v.decision == "NO-GO", v.rationale


def test_derives_yield_on_cost_and_spread():
    d = DealMetrics(name="Derive", noi=5_058_864, total_cost=64_700_000, exit_cap=0.06,
                    levered_irr=0.151, moic=2.02, lease_up_months=9)
    v = score_deal(d)
    assert d.yield_on_cost is not None and abs(d.yield_on_cost - 0.0782) < 0.001
    assert d.dev_spread_bps is not None and d.dev_spread_bps > 150
    assert v.decision == "GO", v.rationale


def test_ranking_orders_go_before_no_go():
    verdicts = rank_deals([_weak_deal(), _strong_like_hamburg()])
    assert verdicts[0].decision == "GO"
    assert verdicts[-1].decision == "NO-GO"


def _run() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())
