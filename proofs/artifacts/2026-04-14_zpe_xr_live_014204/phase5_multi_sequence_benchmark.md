# Phase 5 ContactPose Multi-Sequence Benchmark

## Workload

- dataset: `ContactPose`
- sample archive: `contactpose_sample.zip`
- selected objects: `mug, bowl, camera, binoculars, ps_controller`

## Sequence Results

| Object | Compression vs raw | MPJPE (mm) | Latency (ms) | Packet-loss error (%) | Modern comparator ratio vs ZPE |
|---|---:|---:|---:|---:|---:|
| mug | 24.000x | 0.463 | 0.058 | 0.386 | 0.733x |
| bowl | 23.994x | 0.480 | 0.058 | 0.400 | 0.709x |
| camera | 23.960x | 0.504 | 0.055 | 0.420 | 0.708x |
| binoculars | 23.819x | 0.478 | 0.059 | 0.399 | 0.701x |
| ps_controller | 23.718x | 0.468 | 0.058 | 0.390 | 0.700x |

## Aggregate

- sequence count: `5`
- mean compression vs raw: `23.898x`
- mean MPJPE: `0.479 mm`
- mean latency: `0.057 ms`
- mean packet-loss error: `0.399%`
- modern comparator passes: `0` of `5`
- comparator requirement met: `False`
- sovereign verdict: `PASS`
