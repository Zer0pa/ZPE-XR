# Headset Surrogate Strategy

Phase 3 can stay in silico by building the record contract against surrogate lanes. This is useful only if the record keeps the native gate explicit and fail-closed.

## Immediate In-Silico Stack

1. `synthetic_openxr_fixture`: deterministic fixture shaped like OpenXR/Unity XR Hands data. It drives schema validation, packet/hash-chain checks, and replay-contract tests.
2. `green_movement_prior`: Phase 1's permissive movement-prior lane. It can develop population/session/residual policies but cannot act as headset evidence.
3. `headset_proxy_permissive`: HoloAssist and HO-Cap pressure head/hand/object metadata without pretending to be project-native capture.
4. `headset_proxy_restricted`: HOT3D, EgoDex, EgoMAN/OpenEgo, and similar sources are strong realism references but stay restricted/internal until source terms are resolved.
5. `native_device_capture`: the Phase 5 target. This is the only class that can become `native_verified`.

## Dataset Needs

| Dataset | Phase 3 role | Evidence class |
| --- | --- | --- |
| Synthetic OpenXR fixture | Local schema, validator, replay, and hash-chain testing. | `synthetic_openxr_fixture` |
| KINE-ADL BE-UJI | First green movement-prior lane from Phase 1. | `green_movement_prior` |
| HoloAssist | Permissive headset proxy with head/hands/depth/action annotations. | `headset_proxy_permissive` |
| HO-Cap | HoloLens plus RGB-D hand-object proxy; dataset permissive, toolkit license isolated. | `headset_proxy_permissive` |
| HOT3D | Quest 3/Aria realism reference with hand/object/gaze/SLAM data. | `headset_proxy_restricted` |
| EgoDex | Vision Pro dexterous manipulation realism reference. | `headset_proxy_restricted` |
| OpenEgo / EgoMAN | Standardization and trajectory/intention reference; constituent terms must be checked. | `headset_proxy_restricted` |
| EgoEMG | Future neuromotor/intention lane after license/access lock. | `headset_proxy_restricted` |

## Physics And Nature Pattern

The useful nature-derived pattern is a measurable state-space representation:

- observation model: source timestamps, frame indices, joint locations, validity flags, and coordinate transforms;
- motor invariants: wrist/palm/head/task-relative coordinate frames preserved as derived metadata;
- description length: population prior bytes, session delta bytes, residual stream bytes, and record metadata bytes are accounted separately;
- baselines: DMP, ProMP, Koopman, spline, PCA/FPCA, raw float32, and float16+zlib remain competitors.

The commercial wedge only survives if the record makes downstream embodiment search/replay cheaper, more reliable, or more auditable than ordinary packet compression under matched denominators.

## Phase Boundary

This strategy does not close CAPT-03 or RUNT-01. It creates the contract that future native capture must satisfy.
