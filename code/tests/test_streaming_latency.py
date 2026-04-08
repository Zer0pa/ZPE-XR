from __future__ import annotations

from zpe_xr.example_support import streaming_latency_summary


def test_streaming_latency_stays_sub_millisecond_at_90hz() -> None:
    summary = streaming_latency_summary(num_frames=900, seed=1901, gesture="mixed")

    assert summary["fps"] == 90
    assert summary["frames"] == 900
    assert summary["meets_realtime_budget"] is True
    assert summary["latency_ms"]["combined_avg_ms"] < 1.0
    assert summary["latency_ms"]["combined_p95_ms"] < 1.0
