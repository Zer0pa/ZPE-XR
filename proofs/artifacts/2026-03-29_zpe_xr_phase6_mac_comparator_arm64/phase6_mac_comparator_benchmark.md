# Phase 6 Mac Comparator Benchmark

## Host

- platform: `Darwin 24.5.0`
- machine: `arm64`
- python: `3.14.0`

## Execution Surface

- canonical root: `/Users/Zer0pa/ZPE/ZPE XR`
- root execution surface: `incomplete`
- staged backend: `rust`

## Workload

- kind: `synthetic_frozen_v1`
- frames: `90`
- gesture: `mixed`
- seed: `6607`
- iterations: `60`

## Comparator Matrix

| Comparator | Evidence | Bytes/frame | Compression vs raw | 4-player KB/s @90 | Encode avg ms/frame | Decode avg ms/frame | MPJPE mm |
|---|---|---:|---:|---:|---:|---:|---:|
| ZPE-XR staged package (local Mac) | measured_local | 55.722 | 26.130x | 14.692 | 0.014684 | 0.014757 | 0.878710 |
| Raw OpenXR-like float stream (local proxy) | proxy_measured_local | 1456.000 | 1.000x | 383.906 | 0.000052 | 0.000566 | 0.000000 |
| Modern float16+zlib proxy (local) | proxy_measured_local | 336.100 | 4.332x | 88.620 | 0.051406 | 0.032473 | 0.277196 |
| Photon Fusion XR Hands (doc-derived compressed rotations) | doc_derived_transport_only | 38.000 | 38.316x | 10.020 | — | — | — |
| Photon Fusion XR Hands (doc-derived full quaternion transfer) | doc_derived_transport_only | 772.000 | 1.886x | 203.555 | — | — | — |
| Ultraleap VectorHand compressed encoding | code_derived_transport_only | 172.000 | 8.465x | 45.352 | — | — | — |

## Market References Without Numeric Rows

- `Unity Netcode for GameObjects`: Mainstream networking surface, but no official apples-to-apples XR hand-sync transport or latency row was found. Source: `https://docs.unity3d.com/kr/6000.0/Manual/com.unity.netcode.gameobjects.html`
- `Normcore VR/AR`: Major VR/AR multiplayer product, but no official hand-sync byte or latency table was found. Source: `https://normcore.io/solutions/vr-ar`

## ContactPose Attempt

- status: `executed`
- mean compression vs raw: `56.144x`
- mean MPJPE: `0.479 mm`
- mean latency: `0.028 ms`
- modern comparator passes: `0/5`

## Conclusions

- ZPE-XR now has a same-machine measured Mac row from the staged package surface.
- The raw float stream and the internal modern comparator proxy now have same-machine measured proxy rows, so local latency and overhead are no longer purely inherited from historical artifacts.
- ZPE-XR is smaller than the code-derived Ultraleap VectorHand row on bytes/frame under the frozen two-hand stream semantics.
- Photon remains smaller on the documented compressed transport row, but that row is still narrower in semantics and not a closed head-to-head displacement result.
- Market-popular lanes such as Unity NGO and Normcore still need a runnable same-machine benchmark before they can enter the numeric comparison table.

## Unresolved

- Photon remains transport-only in this phase; no same-machine runtime benchmark closes displacement.
- Ultraleap remains the strongest close-semantics open transport row, but it is still code-derived here rather than locally executed.
- Unity NGO and Normcore remain market references only until a runnable same-machine hand-sync benchmark is added inside this folder.
- The canonical root execution surface is still incomplete if required root package modules remain missing.
