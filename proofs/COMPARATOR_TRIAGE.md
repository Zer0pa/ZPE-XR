# Comparator Triage

This note captures the current comparator worklist for the staged `ZPE-XR/` repo.

It does not change the governing verdict in `proofs/FINAL_STATUS.md`. The public gate remains blocked at `0/5`.

## Exact Currently Instrumented Rows

The runnable staged comparator surface today is:

- `ZPE-XR/code/source/zpe_xr/phase6_benchmarks.py`
- `ZPE-XR/code/scripts/run_phase6_mac_comparator_benchmark.py`
- `ZPE-XR/proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/`

That surface currently measures:

- staged ZPE-XR package row
- raw float stream local proxy
- modern `float16 + zlib` local proxy
- Photon doc-derived compressed row
- Photon doc-derived full quaternion row
- Ultraleap `VectorHand` row
- Unity NGO and Normcore as market-reference-only lanes without numeric rows

## First Tractable Comparator Target

The first runnable closure candidate is the local `modern_float16_delta_plus_zlib_local` comparator lane.

Why:

- it is already instrumented in this repo
- it is CPU-local and does not require a vendor runtime
- it is semantically much closer to the frozen two-hand stream than Photon's narrower articulation row
- it can be re-attacked immediately with new packet/pathology instrumentation

## Current Read Of The Runnable Rows

From `proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.md`:

- ZPE-XR staged row: `55.722 bytes/frame`, `26.130x`, `0.014684 ms` encode, `0.014757 ms` decode, `0.878710 mm`
- modern proxy row: `336.100 bytes/frame`, `4.332x`, `0.051406 ms` encode, `0.032473 ms` decode, `0.277196 mm`
- Photon compressed row: `38.000 bytes/frame` but doc-derived and narrower in semantics
- Ultraleap row: `172.000 bytes/frame`, code-derived transport contract

This makes the actionable question narrow: not “is the public gate solved?”, but “what codec changes could move the closest local proxy lane without breaking the current authority surface?”

## Baseline Family Used For The First Target

The current tractable baseline family in this staged repo is:

- half-float positional deltas
- half-float rotations
- `zlib` packet compression

This is implemented in `phase6_benchmarks.py` as the local modern proxy lane. It is the baseline family used for the first comparator target in this repo. More complex GPU-heavy learned baselines remain open and would run more naturally on the exposed RunPod workspace if they are added later.

## Specific Rust Kernel Changes Worth Trying Next

The most credible next changes are:

1. parent-relative residual coding instead of only absolute or previous-frame world deltas
2. explicit changed-joint bitmasks so static joints stop consuming fixed-width residual entries
3. mixed-width residuals so small updates stay compact and only overflow cases pay the wider cost
4. separate global palm or hand-root motion from finger articulation residuals
5. frame-level pathology logging so keyframe resets, overflows, and concealment behavior can be attacked directly instead of inferred from aggregates

## GPU And Pod Note

The exposed TCP RunPod path is reachable:

- `ssh root@38.80.152.248 -p 33488 -i ~/.ssh/id_ed25519`

The pod has a visible RTX 6000 Ada GPU and a large `/workspace` mount. That is useful for future learned or heavier baseline work. The first tractable comparator target in this staged repo does not require GPU execution.
