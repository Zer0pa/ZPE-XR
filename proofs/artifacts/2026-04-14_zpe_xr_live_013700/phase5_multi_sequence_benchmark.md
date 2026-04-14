# Phase 5 ContactPose Multi-Sequence Benchmark

## Workload

- dataset: `ContactPose`
- sample archive: `contactpose_sample.zip`
- selected objects: `mug, bowl, camera, binoculars, ps_controller`

## Sequence Results

| Object | Compression vs raw | MPJPE (mm) | Latency (ms) | Packet-loss error (%) | Modern comparator ratio vs ZPE |
|---|---:|---:|---:|---:|---:|
| mug | 24.062x | 0.463 | 0.058 | 0.386 | 0.835x |
| bowl | 24.062x | 0.480 | 0.060 | 0.400 | 0.833x |
| camera | 24.062x | 0.504 | 0.056 | 0.420 | 0.832x |
| binoculars | 24.062x | 0.478 | 0.059 | 0.399 | 0.833x |
| ps_controller | 24.062x | 0.468 | 0.059 | 0.390 | 0.835x |

## Aggregate

- sequence count: `5`
- mean compression vs raw: `24.062x`
- mean MPJPE: `0.479 mm`
- mean latency: `0.058 ms`
- mean packet-loss error: `0.399%`
- modern comparator passes: `0` of `5`
- comparator requirement met: `False`
- sovereign verdict: `PASS`
