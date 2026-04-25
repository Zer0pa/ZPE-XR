# Phase 07 Ultraleap Local Benchmark

## Host

- platform: `Darwin 24.5.0`
- machine: `arm64`
- python: `3.14.0`

## Synthetic Benchmark

- frames: `90`
- gesture: `mixed`
- seed: `6607`

| Comparator | Evidence | Bytes/frame | Compression vs raw | 4-player KB/s @90 | Combined latency ms | MPJPE mm | 10% loss error % |
|---|---|---:|---:|---:|---:|---:|---:|
| ZPE-XR canonical root codec | measured_local | 51.622 | 28.205x | 13.611 | 0.055 | 0.879 | 1.010 |
| Ultraleap VectorHand local proxy | proxy_measured_local | 172.000 | 8.465x | 45.352 | 0.227 | 3.365 | 2.848 |

## Synthetic Relative Read

- ZPE smaller on bytes: `True`
- incumbent/ZPE bytes ratio: `3.332x`
- ZPE lower latency: `True`
- ZPE lower MPJPE: `True`

## ContactPose Multi-Sequence

- sample archive: `contactpose_sample.zip`
- selected objects: `mug, bowl, camera, binoculars, ps_controller`

| Object | ZPE bytes/frame | Ultraleap bytes/frame | ZPE latency ms | Ultraleap latency ms | ZPE MPJPE mm | Ultraleap MPJPE mm |
|---|---:|---:|---:|---:|---:|---:|
| mug | 25.933 | 172.000 | 0.024 | 0.139 | 0.463 | 5.213 |
| bowl | 25.933 | 172.000 | 0.023 | 0.193 | 0.480 | 4.881 |
| camera | 25.933 | 172.000 | 0.028 | 0.155 | 0.504 | 3.801 |
| binoculars | 25.933 | 172.000 | 0.023 | 0.139 | 0.478 | 4.984 |
| ps_controller | 25.933 | 172.000 | 0.024 | 0.144 | 0.468 | 3.891 |

## ContactPose Aggregate

- ZPE mean bytes/frame: `25.933`
- Ultraleap mean bytes/frame: `172.000`
- ZPE mean latency: `0.024 ms`
- Ultraleap mean latency: `0.154 ms`
- ZPE mean MPJPE: `0.479 mm`
- Ultraleap mean MPJPE: `4.554 mm`
- ZPE smaller on all sequences: `True`
- ZPE lower latency on mean: `True`
- ZPE lower MPJPE on mean: `True`

## Conclusions

- ZPE-XR remains smaller than the same-machine Ultraleap local proxy on the frozen synthetic lane.
- ZPE-XR has lower measured synthetic latency than the local Ultraleap proxy on this Mac.
- ZPE-XR stays smaller than the local Ultraleap proxy across the executed ContactPose multi-sequence object set.
- Ultraleap is now a same-machine local proxy-measured incumbent row rather than a transport-only placeholder.
