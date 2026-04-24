# ZPE-XR FAQ

## Is ZPE-XR public-release ready?

No. The repo remains `BLOCKED` for public release because the modern comparator gate is still `0/5` and runtime closure remains external.

## What does ZPE-XR prove today?

It proves a deterministic two-hand transport surface on the current ContactPose lane, with sub-millisecond encode+decode latency, byte-identical replay, and bounded MPJPE on the measured object set.

## Do the Ultraleap and Photon rows close vendor displacement?

No. Phase 7 and Phase 8 are same-machine proxy lanes. They are useful evidence, but not full vendor runtime displacement.

## Why is Photon caveated?

The Photon articulation proxy meters a narrower finger articulation payload. Shared per-frame hand-root pose remains outside the metered payload, so it is not equivalent to the frozen full-position stream.

## What is the next product wedge?

After Phase 09-02, the best downstream wedge is a separate private ZPE-Fanmode bridge that maps replayable ZPE-XR-origin inputs into a bounded fan-event vocabulary.
