# Capture Evidence Classes

Phase 3 separates engineering progress from authority. These classes are part of every `EmbodimentRecord` and decide what a record is allowed to prove.

| Class | Meaning | Allowed use | Not allowed |
| --- | --- | --- | --- |
| `synthetic_openxr_fixture` | Generated OpenXR-shaped data with 26 joints per hand and deterministic metadata. | Schema, validator, replay, hash-chain, and denominator harness tests. | Native capture, provider latency, tracking-loss, or commercial authority claims. |
| `green_movement_prior` | Permissive non-headset movement data locked by Phase 1, such as KINE-ADL BE-UJI. | Movement-form priors and calibration-policy development after one-sample structural verification. | Native headset capture claims. |
| `headset_proxy_permissive` | Headset or headset-like proxy corpus with permissive enough terms for internal schema pressure. | Contract pressure for head/hand/device metadata and proxy robustness. | Native runtime closure or sovereign pass. |
| `headset_proxy_restricted` | Strong realism source with custom, noncommercial, or unresolved commercial terms. | Internal research only if terms allow. | Public/commercial authority. |
| `native_device_capture` | User/project-produced Quest, Meta OpenXR, Unity XR Hands, Magic Leap, VIVE, or equivalent runtime capture receipt. | Phase 5 capture/runtime closure when it includes packet log, record hash, replay digest, build metadata, and required motion protocol. | Inference from synthetic or dataset proxy records. |

`native_capture_status` is independent and must be one of:

| Status | Meaning |
| --- | --- |
| `not_applicable` | Used for synthetic, non-headset movement-prior, or proxy records that cannot be native capture. |
| `pending` | A native route is expected but has not produced an admissible receipt. |
| `pilot_not_sovereign` | Native pilot exists but is shorter or weaker than the sovereign capture gate. |
| `native_verified` | Native capture evidence exists. The validator only allows this status with `native_device_capture`. |

CRC32 packet checks are transport checks only. Record provenance must use SHA-256 hash chains or stronger cryptographic hashing.
