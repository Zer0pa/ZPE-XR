# Phase 3 Dataset Access Status

Captured on `2026-04-08` while executing the XR data-enrichment lane.

## ContactPose Full Corpus

- Status: `blocked`
- DOI probe: `https://dx.doi.org/10.21227/fb0w-gt48`
- Landing page: `https://ieee-dataport.org/documents/contactpose-part-1`
- Observed result:
  - DOI resolved to the IEEE DataPort landing page.
  - The landing page was reachable anonymously.
  - The page exposed a time-limited `code.zip` attachment, but this pass did not establish an anonymous bulk dataset archive URL for the full corpus.
- Outcome: the repo keeps the existing ContactPose subset authority and does not claim full-corpus expansion.

## GRAB

- Status: `blocked`
- Landing page: `https://grab.is.tue.mpg.de/`
- Observed result:
  - The homepage was reachable anonymously.
  - The homepage states that registration and license acceptance are required before the dataset download works.
- Outcome: no GRAB benchmark was added during this pass.

## InterHand2.6M

- Status: `complete`
- Artifact: `proofs/artifacts/2026-04-08_zpe_xr_phase3_interhand_realdata/phase3_interhand_benchmark.md`
- Outcome: three real bilateral sequences were benchmarked and anchored in-repo.
