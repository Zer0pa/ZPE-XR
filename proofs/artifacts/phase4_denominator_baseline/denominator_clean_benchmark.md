# Phase 4 Denominator-Clean Benchmark

Schema: `zpe-xr-denominator-baseline-1`
Evidence class: `synthetic_openxr_fixture`
Native capture status: `not_applicable`
Native capture claim: `false`

This is in-silico denominator pressure only. It does not satisfy native headset capture.

## Segment Rows

| Segment | Row | Status | Bytes/frame | Total bytes | Denominator |
| --- | --- | ---: | ---: | ---: | --- |
| static_hold | `raw_21xyz` | not_applicable | not_available | not_available | not_applicable_for_26_joint_source_layout |
| static_hold | `raw_26xyz` | measured | 624.000 | 7488 | 26 joints/hand x 2 hands x xyz float32 |
| static_hold | `raw_26xyzquat` | measured | 1456.000 | 17472 | 26 joints/hand x 2 hands x xyz+quat float32 |
| static_hold | `raw_openxr_like_location` | measured | 2080.000 | 24960 | OpenXR-like XrHandJointLocationEXT fields |
| static_hold | `float16_zlib_xyz` | measured | 171.000 | 2052 | 26 joints/hand x 2 hands x xyz float16 zlib |
| static_hold | `float16_zlib_xyzquat` | measured | 187.667 | 2252 | 26 joints/hand x 2 hands x xyzquat float16 zlib |
| static_hold | `zpe_stream_container` | measured | 51.750 | 621 | ZXRS stream container wrapping ZPE packets |
| static_hold | `zpe_packet_stream` | measured | 47.000 | 564 | ZPE packet payload bytes only |
| static_hold | `zpe_embodiment_record` | measured | 681.417 | 8177 | EmbodimentRecord JSON plus ZXRS packet stream |
| static_hold | `photon_xrhands_proxy` | measured | 38.000 | 456 | Photon XR Hands doc-derived compressed rotations proxy |
| static_hold | `ultraleap_vectorhand_proxy` | measured | 172.000 | 2064 | Ultraleap VectorHand open-source bytes proxy |
| static_hold | `zpe_adaptive_hybrid` | not_available | not_available | not_available | not_available_until_prior_session_residual_bytes_are_separated |
| slow_manipulation | `raw_21xyz` | not_applicable | not_available | not_available | not_applicable_for_26_joint_source_layout |
| slow_manipulation | `raw_26xyz` | measured | 624.000 | 7488 | 26 joints/hand x 2 hands x xyz float32 |
| slow_manipulation | `raw_26xyzquat` | measured | 1456.000 | 17472 | 26 joints/hand x 2 hands x xyz+quat float32 |
| slow_manipulation | `raw_openxr_like_location` | measured | 2080.000 | 24960 | OpenXR-like XrHandJointLocationEXT fields |
| slow_manipulation | `float16_zlib_xyz` | measured | 176.750 | 2121 | 26 joints/hand x 2 hands x xyz float16 zlib |
| slow_manipulation | `float16_zlib_xyzquat` | measured | 199.167 | 2390 | 26 joints/hand x 2 hands x xyzquat float16 zlib |
| slow_manipulation | `zpe_stream_container` | measured | 52.750 | 633 | ZXRS stream container wrapping ZPE packets |
| slow_manipulation | `zpe_packet_stream` | measured | 48.000 | 576 | ZPE packet payload bytes only |
| slow_manipulation | `zpe_embodiment_record` | measured | 682.917 | 8195 | EmbodimentRecord JSON plus ZXRS packet stream |
| slow_manipulation | `photon_xrhands_proxy` | measured | 38.000 | 456 | Photon XR Hands doc-derived compressed rotations proxy |
| slow_manipulation | `ultraleap_vectorhand_proxy` | measured | 172.000 | 2064 | Ultraleap VectorHand open-source bytes proxy |
| slow_manipulation | `zpe_adaptive_hybrid` | not_available | not_available | not_available | not_available_until_prior_session_residual_bytes_are_separated |
| active_reaching | `raw_21xyz` | not_applicable | not_available | not_available | not_applicable_for_26_joint_source_layout |
| active_reaching | `raw_26xyz` | measured | 624.000 | 7488 | 26 joints/hand x 2 hands x xyz float32 |
| active_reaching | `raw_26xyzquat` | measured | 1456.000 | 17472 | 26 joints/hand x 2 hands x xyz+quat float32 |
| active_reaching | `raw_openxr_like_location` | measured | 2080.000 | 24960 | OpenXR-like XrHandJointLocationEXT fields |
| active_reaching | `float16_zlib_xyz` | measured | 179.250 | 2151 | 26 joints/hand x 2 hands x xyz float16 zlib |
| active_reaching | `float16_zlib_xyzquat` | measured | 203.417 | 2441 | 26 joints/hand x 2 hands x xyzquat float16 zlib |
| active_reaching | `zpe_stream_container` | measured | 80.083 | 961 | ZXRS stream container wrapping ZPE packets |
| active_reaching | `zpe_packet_stream` | measured | 75.333 | 904 | ZPE packet payload bytes only |
| active_reaching | `zpe_embodiment_record` | measured | 710.083 | 8521 | EmbodimentRecord JSON plus ZXRS packet stream |
| active_reaching | `photon_xrhands_proxy` | measured | 38.000 | 456 | Photon XR Hands doc-derived compressed rotations proxy |
| active_reaching | `ultraleap_vectorhand_proxy` | measured | 172.000 | 2064 | Ultraleap VectorHand open-source bytes proxy |
| active_reaching | `zpe_adaptive_hybrid` | not_available | not_available | not_available | not_available_until_prior_session_residual_bytes_are_separated |
| fast_translation | `raw_21xyz` | not_applicable | not_available | not_available | not_applicable_for_26_joint_source_layout |
| fast_translation | `raw_26xyz` | measured | 624.000 | 7488 | 26 joints/hand x 2 hands x xyz float32 |
| fast_translation | `raw_26xyzquat` | measured | 1456.000 | 17472 | 26 joints/hand x 2 hands x xyz+quat float32 |
| fast_translation | `raw_openxr_like_location` | measured | 2080.000 | 24960 | OpenXR-like XrHandJointLocationEXT fields |
| fast_translation | `float16_zlib_xyz` | measured | 175.000 | 2100 | 26 joints/hand x 2 hands x xyz float16 zlib |
| fast_translation | `float16_zlib_xyzquat` | measured | 195.750 | 2349 | 26 joints/hand x 2 hands x xyzquat float16 zlib |
| fast_translation | `zpe_stream_container` | measured | 187.417 | 2249 | ZXRS stream container wrapping ZPE packets |
| fast_translation | `zpe_packet_stream` | measured | 182.667 | 2192 | ZPE packet payload bytes only |
| fast_translation | `zpe_embodiment_record` | measured | 817.500 | 9810 | EmbodimentRecord JSON plus ZXRS packet stream |
| fast_translation | `photon_xrhands_proxy` | measured | 38.000 | 456 | Photon XR Hands doc-derived compressed rotations proxy |
| fast_translation | `ultraleap_vectorhand_proxy` | measured | 172.000 | 2064 | Ultraleap VectorHand open-source bytes proxy |
| fast_translation | `zpe_adaptive_hybrid` | not_available | not_available | not_available | not_available_until_prior_session_residual_bytes_are_separated |
| pointing | `raw_21xyz` | not_applicable | not_available | not_available | not_applicable_for_26_joint_source_layout |
| pointing | `raw_26xyz` | measured | 624.000 | 7488 | 26 joints/hand x 2 hands x xyz float32 |
| pointing | `raw_26xyzquat` | measured | 1456.000 | 17472 | 26 joints/hand x 2 hands x xyz+quat float32 |
| pointing | `raw_openxr_like_location` | measured | 2080.000 | 24960 | OpenXR-like XrHandJointLocationEXT fields |
| pointing | `float16_zlib_xyz` | measured | 177.000 | 2124 | 26 joints/hand x 2 hands x xyz float16 zlib |
| pointing | `float16_zlib_xyzquat` | measured | 197.833 | 2374 | 26 joints/hand x 2 hands x xyzquat float16 zlib |
| pointing | `zpe_stream_container` | measured | 53.083 | 637 | ZXRS stream container wrapping ZPE packets |
| pointing | `zpe_packet_stream` | measured | 48.333 | 580 | ZPE packet payload bytes only |
| pointing | `zpe_embodiment_record` | measured | 682.500 | 8190 | EmbodimentRecord JSON plus ZXRS packet stream |
| pointing | `photon_xrhands_proxy` | measured | 38.000 | 456 | Photon XR Hands doc-derived compressed rotations proxy |
| pointing | `ultraleap_vectorhand_proxy` | measured | 172.000 | 2064 | Ultraleap VectorHand open-source bytes proxy |
| pointing | `zpe_adaptive_hybrid` | not_available | not_available | not_available | not_available_until_prior_session_residual_bytes_are_separated |
| grasp_release | `raw_21xyz` | not_applicable | not_available | not_available | not_applicable_for_26_joint_source_layout |
| grasp_release | `raw_26xyz` | measured | 624.000 | 7488 | 26 joints/hand x 2 hands x xyz float32 |
| grasp_release | `raw_26xyzquat` | measured | 1456.000 | 17472 | 26 joints/hand x 2 hands x xyz+quat float32 |
| grasp_release | `raw_openxr_like_location` | measured | 2080.000 | 24960 | OpenXR-like XrHandJointLocationEXT fields |
| grasp_release | `float16_zlib_xyz` | measured | 174.500 | 2094 | 26 joints/hand x 2 hands x xyz float16 zlib |
| grasp_release | `float16_zlib_xyzquat` | measured | 194.667 | 2336 | 26 joints/hand x 2 hands x xyzquat float16 zlib |
| grasp_release | `zpe_stream_container` | measured | 51.417 | 617 | ZXRS stream container wrapping ZPE packets |
| grasp_release | `zpe_packet_stream` | measured | 46.667 | 560 | ZPE packet payload bytes only |
| grasp_release | `zpe_embodiment_record` | measured | 681.250 | 8175 | EmbodimentRecord JSON plus ZXRS packet stream |
| grasp_release | `photon_xrhands_proxy` | measured | 38.000 | 456 | Photon XR Hands doc-derived compressed rotations proxy |
| grasp_release | `ultraleap_vectorhand_proxy` | measured | 172.000 | 2064 | Ultraleap VectorHand open-source bytes proxy |
| grasp_release | `zpe_adaptive_hybrid` | not_available | not_available | not_available | not_available_until_prior_session_residual_bytes_are_separated |
| occlusion_jitter | `raw_21xyz` | not_applicable | not_available | not_available | not_applicable_for_26_joint_source_layout |
| occlusion_jitter | `raw_26xyz` | measured | 624.000 | 7488 | 26 joints/hand x 2 hands x xyz float32 |
| occlusion_jitter | `raw_26xyzquat` | measured | 1456.000 | 17472 | 26 joints/hand x 2 hands x xyz+quat float32 |
| occlusion_jitter | `raw_openxr_like_location` | measured | 2080.000 | 24960 | OpenXR-like XrHandJointLocationEXT fields |
| occlusion_jitter | `float16_zlib_xyz` | measured | 177.667 | 2132 | 26 joints/hand x 2 hands x xyz float16 zlib |
| occlusion_jitter | `float16_zlib_xyzquat` | measured | 201.500 | 2418 | 26 joints/hand x 2 hands x xyzquat float16 zlib |
| occlusion_jitter | `zpe_stream_container` | measured | 82.417 | 989 | ZXRS stream container wrapping ZPE packets |
| occlusion_jitter | `zpe_packet_stream` | measured | 77.667 | 932 | ZPE packet payload bytes only |
| occlusion_jitter | `zpe_embodiment_record` | measured | 712.500 | 8550 | EmbodimentRecord JSON plus ZXRS packet stream |
| occlusion_jitter | `photon_xrhands_proxy` | measured | 38.000 | 456 | Photon XR Hands doc-derived compressed rotations proxy |
| occlusion_jitter | `ultraleap_vectorhand_proxy` | measured | 172.000 | 2064 | Ultraleap VectorHand open-source bytes proxy |
| occlusion_jitter | `zpe_adaptive_hybrid` | not_available | not_available | not_available | not_available_until_prior_session_residual_bytes_are_separated |
| hand_controller_transition_or_tracking_loss | `raw_21xyz` | not_applicable | not_available | not_available | not_applicable_for_26_joint_source_layout |
| hand_controller_transition_or_tracking_loss | `raw_26xyz` | measured | 624.000 | 7488 | 26 joints/hand x 2 hands x xyz float32 |
| hand_controller_transition_or_tracking_loss | `raw_26xyzquat` | measured | 1456.000 | 17472 | 26 joints/hand x 2 hands x xyz+quat float32 |
| hand_controller_transition_or_tracking_loss | `raw_openxr_like_location` | measured | 2080.000 | 24960 | OpenXR-like XrHandJointLocationEXT fields |
| hand_controller_transition_or_tracking_loss | `float16_zlib_xyz` | measured | 180.250 | 2163 | 26 joints/hand x 2 hands x xyz float16 zlib |
| hand_controller_transition_or_tracking_loss | `float16_zlib_xyzquat` | measured | 200.000 | 2400 | 26 joints/hand x 2 hands x xyzquat float16 zlib |
| hand_controller_transition_or_tracking_loss | `zpe_stream_container` | measured | 49.750 | 597 | ZXRS stream container wrapping ZPE packets |
| hand_controller_transition_or_tracking_loss | `zpe_packet_stream` | measured | 45.000 | 540 | ZPE packet payload bytes only |
| hand_controller_transition_or_tracking_loss | `zpe_embodiment_record` | measured | 682.083 | 8185 | EmbodimentRecord JSON plus ZXRS packet stream |
| hand_controller_transition_or_tracking_loss | `photon_xrhands_proxy` | measured | 38.000 | 456 | Photon XR Hands doc-derived compressed rotations proxy |
| hand_controller_transition_or_tracking_loss | `ultraleap_vectorhand_proxy` | measured | 172.000 | 2064 | Ultraleap VectorHand open-source bytes proxy |
| hand_controller_transition_or_tracking_loss | `zpe_adaptive_hybrid` | not_available | not_available | not_available | not_available_until_prior_session_residual_bytes_are_separated |

## Aggregate Rows

| Row | Status | Bytes/frame | Total bytes |
| --- | ---: | ---: | ---: |
| `float16_zlib_xyz` | measured | 176.427 | 16937 |
| `float16_zlib_xyzquat` | measured | 197.500 | 18960 |
| `photon_xrhands_proxy` | measured | 38.000 | 3648 |
| `raw_21xyz` | not_applicable | not_available | not_available |
| `raw_26xyz` | measured | 624.000 | 59904 |
| `raw_26xyzquat` | measured | 1456.000 | 139776 |
| `raw_openxr_like_location` | measured | 2080.000 | 199680 |
| `ultraleap_vectorhand_proxy` | measured | 172.000 | 16512 |
| `zpe_adaptive_hybrid` | not_available | not_available | not_available |
| `zpe_embodiment_record` | measured | 706.281 | 67803 |
| `zpe_packet_stream` | measured | 71.333 | 6848 |
| `zpe_stream_container` | measured | 76.083 | 7304 |

## Gate Consequence

- Phase 4 status: denominator-clean measurement pressure exists for synthetic/proxy execution only.
- Phase 5 native capture remains pending.
- Adaptive-hybrid advantage remains unproved; the row is explicitly `not_available` until prior/session/residual bytes are separated.
