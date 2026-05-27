# ZPE-XR

> Product-page mirror for `/encoding/ZPE-XR/`.
> Live public repo: [Zer0pa/ZPE-XR](https://github.com/Zer0pa/ZPE-XR).
> GitHub Markdown cannot reproduce the website typography, CSS, JavaScript, scroll behavior, or live bento layout; this README translates the product page into GitHub-safe Markdown evidence blocks.

## 0. Install / Developer Commands

The product page is the positioning authority. This section is the only retained developer-surface material from the previous root README.

```bash
Deterministic XR transport codec. Two-hand joint streams target packet size, transport determinism, and replay behavior. Install from PyPI: `pip install zpe-xr
pip install zpe-xr
git clone https://github.com/Zer0pa/ZPE-XR.git zpe-xr
python -m pip install "./code[dev]"
python -m pytest ./code/tests -q
```

## Product Page Mirror

**Product-page title:** ZPE-XR · ContactPose hand-stream transport · Zer0pa

**Product-page description:** ZPE-XR · deterministic ContactPose transport · 25.9 B/frame, 0.057 ms encode+decode, 0.479 mm MPJPE · comparator gate 0/5 · PyPI zpe-xr 0.3.1 stale

### Hero Translation

> 00 · ZPE-XR · MOTION TRANSPORTRESEARCH-READY · COMPARATOR 0/5 Hands that travel, byte for byte. Two-hand pose transport codec · zpe-xr v0.3.1 · github.com/Zer0pa/ZPE-XR In a VR session your hands are always moving — picking up, pointing, reaching across a room. Today that motion is a stream of raw floats, expensive on the network and erased the moment the session ends. ZPE-XR is a different answer: a sealed 25.9-byte packet for two complete hands per frame, decoded in 0.057 ms to byte-identical output on any machine, any year. The transport works on ContactPose. Unity and Meta runtime integration is still external; float16+zlib still wins raw fidelity by 0.2 mm.

## Positioning

| Field | Value |
| --- | --- |
| Section | encoding |
| Product route | /encoding/ZPE-XR/ |
| Live public repository | https://github.com/Zer0pa/ZPE-XR |
| Repo identity used here | ZPE-XR |
| Website display identity | ZPE-XR |
| Verdict | BLOCKED |
| Posture | always_in_beta |
| Headline metric | Compression vs raw: 23.90x. ZPE-XR canonical authority surface; useful now, improving continuously. |
| Honest blocker | No public release readiness.; No Unity or Meta runtime closure.; No Photon displacement claim. |
| Mechanics asset from product page | XR.gif |

## Key Metrics

| Metric | Value | Baseline |
| --- | --- | --- |
| Compression vs raw | 23.90x | Ultraleap 8.47x |
| Mean position error | 0.479 mm MPJPE | float16+zlib 0.277 mm (better fidelity) |
| Encode+decode latency | 0.057 ms mean | float16+zlib 0.084 ms |
| Bytes/frame vs Ultraleap | 25.9 vs 172.0 (6.63x smaller) | Ultraleap VectorHand local proxy |

## Proof Anchors

| Path | State |
| --- | --- |
| proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json | VERIFIED |
| proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_surface_adjudication.md | VERIFIED |
| proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_release_decision.md | VERIFIED |
| proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json | VERIFIED |
| proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.json | VERIFIED |
| proofs/artifacts/2026-03-29_zpe_xr_phase7_ultraleap_local/phase7_ultraleap_local_benchmark.json | VERIFIED |

## What We Prove

- The zpe-xr package and repo install surfaces are real.
- The current ContactPose rerun proves 23.90x compression vs raw, 0.057 ms mean encode+decode latency, and 0.479 mm mean position error on the selected five-sequence lane.
- Byte-identical replay is part of the carried transport surface.
- The cold-start audit and release-decision packet are present and live in the repo.
- Same-machine proxy lanes exist for Ultraleap VectorHand and Photon Fusion XR Hands, with Photon still narrower than the frozen full-position stream.
- The repo can tell the truth about strong transport behavior without pretending comparator superiority or runtime closure.

## What We Do Not Claim

- No public release readiness.
- No Unity or Meta runtime closure.
- No Photon displacement claim.
- No exact PRD-corpus closure claim.
- No broad hand-tracking superiority claim.

## Blockers / Failures

> No public release readiness.; No Unity or Meta runtime closure.; No Photon displacement claim.

## Verification Surface

| Code | Check | Verdict |
| --- | --- | --- |
| V_01 | ContactPose benchmark lane | PASS |
| V_02 | Package mechanics | PASS |
| V_03 | Cold-start audit | PASS |
| V_04 | Modern comparator gate | FAIL |
| V_05 | XR-C007 runtime closure | INC |
| V_06 | Public release readiness | FAIL |

## License

| Field | Value |
| --- | --- |
| License | SAL-7.0 |
| Authority source | README.md |

## Upcoming Workstreams

| Category | Summary |
| --- | --- |
| Research-Deferred — Investigation Underway | Float16+zlib fidelity gap closure. Current 0.479 mm MPJPE vs comparator 0.277 mm; primitive-level investigation into pose-component quantization tradeoffs. Public release blocked until this closes. |
| Operations / External Dependency | Unity / Meta runtime closure. Vendor integration shape (native plugin vs network bridge) under exploration; PRIVATE_ONLY remains correct posture meanwhile. |

## Related Repos

No related repos are declared on the product page frontmatter.

<details>
<summary>Full Visible Product-Page Bento Translation</summary>

This section preserves the product page cells as Markdown text blocks. It intentionally omits shared site navigation, footer chrome, CSS, and scripts.

### Bento Cell 1

> 00 · ZPE-XR · MOTION TRANSPORTRESEARCH-READY · COMPARATOR 0/5 Hands that travel, byte for byte. Two-hand pose transport codec · zpe-xr v0.3.1 · github.com/Zer0pa/ZPE-XR In a VR session your hands are always moving — picking up, pointing, reaching across a room. Today that motion is a stream of raw floats, expensive on the network and erased the moment the session ends. ZPE-XR is a different answer: a sealed 25.9-byte packet for two complete hands per frame, decoded in 0.057 ms to byte-identical output on any machine, any year. The transport works on ContactPose. Unity and Meta runtime integration is still external; float16+zlib still wins raw fidelity by 0.2 mm.

### Bento Cell 2

> 01 · THE GAPARRIVED WRONG VR hands arrive late or too large — the experience breaks before the scene does.

### Bento Cell 3

> 02 · MARKETSADJACENT FORECASTS Release postureBLOCKED Hand tracking solutions$10.9B '33 Extended Reality market$59.2B '31 Spatial computing$280B '28 Ultraleap ref revenue~$30M Hand tracking 19.7% CAGR through 2033; XR 41% CAGR to 2031. Transport is the wire all of it runs on.

### Bento Cell 4

> 03 · VALUE 23.9× Smaller than a raw two-hand frame · 6.63× smaller than Ultraleap VectorHand

### Bento Cell 5

> 04 · INSIGHT A hand in motion is data that needs to travel.

### Bento Cell 6

> 05.1 · CURRENT TECHFLOAT STREAM AND ZLIB XR developers ship hand motion as raw float streams or float16+zlib. Both move bytes. Neither is a transport: no sealed packet, no sequence numbering, no loss recovery, no byte-identical replay, no record after the session ends.

### Bento Cell 7

> 05.2 · OUR TECHSEALED PACKETS ZPE-XR encodes two complete hands — 21 joints each — as a sealed, CRC32-checked packet at 25.9 bytes per frame, 23.9× smaller than raw. A backup sequence number recovers from drops without a keyframe stall. Encode plus decode runs in 0.057 ms, and every recorded ContactPose stream plays back the same hands on any machine, any year.

### Bento Cell 8

> 05.3 · BENCHMARKSCONTACTPOSE MEASURED Compression23.9×vs raw Enc+dec0.057ms MPJPE0.479mm Comparator0/5fidelity Transport sizePASS Round-trip speedPASS FidelityMISS Scope: ContactPose 5-sequence, 3,500 frames. Transport passes. Fidelity comparator 0/5.

### Bento Cell 9

> 06 · MEASUREMENTTRANSPORT VS FIDELITY Every transport number ships next to a fidelity reading.

### Bento Cell 10

> 06.1 · COMPARATIVE PERFORMANCECONTACTPOSE BYTES PER FRAME ZPE-XR25.9 bytes/frame float16+zlib~110 bytes/frame raw float32619.5 bytes/frame comparator fidelity0/5 ContactPose five-sequence run, 3,500 frames. ZPE-XR ships 25.9 bytes per two-hand frame — 6.63× under Ultraleap, 1.47× under Photon Fusion. float16+zlib still wins raw fidelity: 0.277 mm vs 0.479 mm MPJPE — comparator 0/5.

### Bento Cell 11

> 07 · KEY METRICSMEASURED RESULTS

### Bento Cell 12

> 07.1 · VS RAW 23.9× vs raw float32 · ContactPose two-hand comparator

### Bento Cell 13

> 07.2 · BYTES / FRAME 25.9B two complete hands · 6.63× smaller than Ultraleap

### Bento Cell 14

> 07.3 · ENC + DEC 0.057ms encode + decode mean · 3,500-frame ContactPose run

### Bento Cell 15

> 07.4 · MPJPE 0.479mm ZPE-XR vs 0.277 mm float16+zlib · fidelity comparator 0/5

### Bento Cell 16

> 07.5 · LOSS @ 10% 0.399% pose error at 10% loss · 9.5× more resilient than Ultraleap proxy

### Bento Cell 17

> 08 · DETERMINISMBOUNDED REPLAY Packets replay identically. Deployment evidence stays external.

### Bento Cell 18

> 08.1 · WHAT REPLAYS EXACTLYCONTACTPOSE SURFACE On the measured ContactPose surface — five sequences, 3,500 frames — every ZPE-XR packet carries a CRC32 tail and a backup sequence number. The recorded stream decodes byte-for-byte the same on any machine, any year. The checksum is a provenance anchor, not just an error detector. The determinism claim is bounded to the encoded stream — not to the sensor estimating the hand or the engine smoothing the output. float16+zlib still wins raw fidelity: 0.277 mm versus 0.479 mm MPJPE. Comparator 0/5; closing that gap is active research.

### Bento Cell 19

> 08.2 · THE FIDELITY GAP Honest Blocker · float16+zlib wins fidelity (0.277 mm vs 0.479 mm). Comparator 0/5. Unity and Meta runtime closure is externally dependent. Photon Fusion semantic parity remains an open secondary. Replay-error corpus evidence beyond ContactPose is unresolved. PyPI zpe-xr 0.3.1 stale; 0.3.2 pending.

### Bento Cell 20

> 09 WHEN HANDS BECOME PERSISTENT DATA.

### Bento Cell 21

> 09.1 · THE AMBITION Embodiment in XR has been disposable. ZPE-XR makes it the opposite: a sealed packet small enough to network at chat-app bandwidth, faithful enough to play back as the same hands every time, and structured enough to search across recordings. Headsets, robots, archives, and training corpora share one transport for motion.

### Bento Cell 22

> 09.2 · WHAT WORKS NOW A ContactPose-bounded transport: 25.9 bytes per two-hand frame, 0.057 ms round-trip, byte-identical replay under packet loss.

### Bento Cell 23

> 09.3 · WHAT'S STILL OPEN Raw fidelity against float16+zlib, Unity and Meta runtime closure, Photon semantic parity, broader corpora, and the 0.3.2 release.

### Bento Cell 24

> 09.4 · TELEPRESENCE · NEAR-TERM (12–24 MO) Multiplayer hands at messaging-app bandwidth A four-player social session at 90 fps fits inside 6.84 KB/s — the bandwidth budget of a chat app, not a video call. Social-VR studios stop paying a voice-call price just to render fingers, and continuous embodied presence becomes a default rather than a feature.

### Bento Cell 25

> 09.5 · ARCHIVES · NEAR-TERM (12–24 MO) Embodied sessions become persistent records A two-hour session compresses to roughly 49 MB with no fidelity drift on replay. Coaching reviews, surgical rehearsal, factory walkthroughs, and forensic playback stop ending when the headset comes off. Embodiment graduates from disposable runtime state into a scrubable, hash-addressable record.

### Bento Cell 26

> 09.6 · MOTION SEARCH · MID-TERM (24–48 MO) Hand motion becomes a queryable corpus Once every frame is hashed and every gesture fingerprinted, recorded sessions become a search surface. “Find every clip where two hands hand off a mug” turns into a tractable query. Coaches, ergonomists, and rehab clinicians get a search bar over embodied behavior.

### Bento Cell 27

> 09.7 · HUMAN-ROBOT REPLAY · MID-TERM (24–48 MO) Headset hands and robot arms share a clock When a human demonstration and a robot re-run share one packet format, imitation-learning pipelines and teleoperation review collapse into a single timeline with one parity hash. Human-in-the-loop robotics gets a common ground truth where today it has two stacks talking past each other.

### Bento Cell 28

> 09.8 · PHYSICAL AI · PARADIGM (48 MO+) Embodiment becomes network infrastructure The same 26-byte envelope that carries a human hand can carry a robot manipulator across headsets, simulators, training agents, and forensic archives without rewriting at each boundary. Spatial computing stops treating presence as a per-engine reconstruction problem; the network itself carries embodiment as a first-class signal.

</details>

---

Source mapping: product route `/encoding/ZPE-XR/` -> live public repo `Zer0pa/ZPE-XR`. README generated from product-page authority plus retained install/dev commands only.
