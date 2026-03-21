# Phase 4 ContactPose Benchmark

## Workload

- dataset: `ContactPose`
- sample archive: `contactpose_sample.zip`
- selected member: `ContactPose sample data/grasps.zip::grasps/full36_use/binoculars.zip::binoculars/annotations.json`
- object: `binoculars`
- frames used: `90`

## Metrics

- compression vs raw: `56.144x`
- MPJPE: `0.478 mm`
- combined latency: `0.025 ms`
- pose error at 10% loss: `0.399%`
- modern comparator ratio vs ZPE: `0.833x`

## Acceptance

- sovereign verdict: `PASS`
- order of magnitude vs raw: `True`
- fidelity floor: `True`
- latency floor: `True`
- packet-loss floor: `True`
- secondary modern-comparator check: `False`
