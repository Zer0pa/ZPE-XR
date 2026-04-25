# Phase 08 Photon Local Benchmark

## Host

- platform: `Darwin 24.5.0`
- machine: `arm64`
- python: `3.14.0`

## Synthetic Benchmark

- synthetic frames: `90`

| Comparator | Evidence | Bytes/frame | Compression vs raw | 4-player KB/s @90 | Combined latency ms | MPJPE mm | 10% loss error % |
|---|---|---:|---:|---:|---:|---:|---:|
| ZPE-XR canonical root codec | measured_local | 51.622 | 28.205x | 13.611 | 0.069 | 0.879 | 1.010 |
| Photon Fusion XR Hands local articulation proxy | proxy_measured_local | 38.000 | 38.316x | 10.020 | 0.292 | 1.846 | 1.550 |

## Synthetic Relative Read

- ZPE smaller on bytes: `False`
- incumbent/ZPE bytes ratio: `0.736x`
- ZPE lower latency: `True`
- ZPE lower MPJPE: `True`

## ContactPose Multi-Sequence

- sample archive: `contactpose_sample.zip`
- selected objects: `mug, bowl, camera, binoculars, ps_controller`

| Object | ZPE bytes/frame | Photon bytes/frame | ZPE latency ms | Photon latency ms | ZPE MPJPE mm | Photon MPJPE mm |
|---|---:|---:|---:|---:|---:|---:|
| mug | 25.933 | 38.000 | 0.024 | 0.160 | 0.463 | 9.530 |
| bowl | 25.933 | 38.000 | 0.026 | 0.250 | 0.480 | 12.391 |
| camera | 25.933 | 38.000 | 0.023 | 0.163 | 0.504 | 6.100 |
| binoculars | 25.933 | 38.000 | 0.023 | 0.161 | 0.478 | 8.974 |
| ps_controller | 25.933 | 38.000 | 0.024 | 0.162 | 0.468 | 16.422 |

## ContactPose Aggregate

- ZPE mean bytes/frame: `25.933`
- Photon mean bytes/frame: `38.000`
- ZPE mean latency: `0.024 ms`
- Photon mean latency: `0.179 ms`
- ZPE mean MPJPE: `0.479 mm`
- Photon mean MPJPE: `10.683 mm`
- ZPE smaller on all sequences: `True`
- ZPE lower latency on mean: `True`
- ZPE lower MPJPE on mean: `True`

## Conclusions

- Photon remains smaller on bytes/frame than ZPE-XR because the articulation proxy meters only the 19-byte-per-hand finger stream.
- ZPE-XR has lower measured synthetic latency than the local Photon articulation proxy on this Mac.
- Photon is now a same-machine proxy-measured incumbent row rather than a doc-only transport placeholder.
- ZPE-XR retains lower mean ContactPose MPJPE than the local Photon articulation proxy.
- This Phase 08 row stays narrower than the frozen full-position stream because shared per-frame hand-root pose remains outside the metered payload.
