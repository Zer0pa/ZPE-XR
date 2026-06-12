<!--
README refresh proposal for the repo-root README.
Live README file intentionally untouched.
Source README word count at drafting: 1,505.
Proposed body keeps the same Markdown section structure and uses fresher Phase 4 claim boundaries.
-->
# ZPE-XR

## Package Install

Installable package: `python3.11 -m pip install zpe-xr`.
Current release: `0.3.1` on [PyPI](https://pypi.org/project/zpe-xr/).
Source: [Zer0pa/ZPE-XR](https://github.com/Zer0pa/ZPE-XR/).

```bash
python3.11 -m pip install zpe-xr
```

For full install, smoke, source, and developer commands, [click here](#install-developer-commands-detailed).

---

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><span><b>00 · ZPE-XR</b> · MOTION LEDGER</span> <span>RESEARCH-READY · NATIVE PENDING</span></div>
      <h1>Denominator-Clean Hand Motion <span>for XR Transport</span></h1>
      <p>Two-hand pose transport codec and measurement harness · <em>zpe-xr v0.3.1</em> · github.com/Zer0pa/ZPE-XR</p>
      <p>ZPE-XR now has a fail-closed denominator and baseline engine for XR hand-motion records. It separates raw 26-joint xyz, raw xyz+quat, float16+zlib, packet-stream bytes, full EmbodimentRecord bytes, and provenance overhead at segment level. The current evidence is in-silico and proxy-bounded. Native headset capture, adaptive-hybrid advantage, runtime closure, and novelty remain unproved.</p>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<figure>
        <div><img src="docs/assets/product-page-mechanics.gif" alt="ZPE-XR approved scientific square mechanics diagram showing two-hand transport codec mechanics."></div>
        <figcaption><b>Scope:</b> denominator-clean synthetic OpenXR fixture plus historical ContactPose transport. Native capture is still Phase 5 authority.</figcaption>
      </figure>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>01 · THE GAP</b> <span>CLAIMS ARRIVE TOO EARLY</span></div>
      <h2>XR hand streams need smaller packets, but first they need <span>honest denominators.</span></h2>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>02 · MARKETS</b> <span>EVIDENCE BEFORE SCALE</span></div>
      <div>
        <div>
          <div><span>Release posture</span>  <span>BLOCKED</span></div>
          <div><span>Denominator engine</span>  <span>PHASE 4 PASS</span></div>
          <div><span>Native headset capture</span>  <span>PHASE 5</span></div>
          <div><span>Adaptive hybrid</span>  <span>NOT AVAILABLE</span></div>
          <div><span>Public package</span>  <span>v0.3.1</span></div>
        </div>
      </div>
      <div>The commercial wedge is not a slogan yet. It is repeatable measurement pressure: bytes, replay, provenance, and baselines separated before any enterprise claim scales.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="50%" valign="top">
<div><b>03 · VALUE OF MARKET</b></div>
      <div>71.3<span>B</span></div>
      <div>ZPE packet stream · <b>synthetic 26-joint fixture aggregate</b></div>
</td>
<td width="50%" valign="top">
<div><b>04 · INSIGHT</b></div>
      <h2>A hand in motion is <span>evidence before it is a product.</span></h2>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="50%" valign="top">
<div><b>05.1 · CURRENT TECH</b> <span>FLOAT STREAMS AND CLAIM DRIFT</span></div>
        <p>XR hand motion often appears as raw float streams, float16+zlib payloads, or vendor-specific articulation proxies. Without clean denominator rows, xyz and xyz+quat results mix, packet bytes blur into record bytes, and provenance cost disappears from the story.</p>
</td>
<td width="50%" valign="top">
<div><b>05.2 · OUR TECH</b> <span>FAIL-CLOSED ROWS</span></div>
        <p>ZPE-XR reports segment-level rows for raw_26xyz, raw_26xyzquat, float16+zlib xyz, float16+zlib xyzquat, ZPE packet streams, stream containers, and full EmbodimentRecords. It rejects ratios without denominators, surrogate-native upgrades, CRC32 provenance, aggregate-only reports, and adaptive-hybrid rows with unseparated bytes.</p>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>05.3 · BENCHMARKS</b> <span>PHASE 4 DENOMINATOR-CLEAN</span></div>
      <div>
        <div>
          <div><span>raw_26xyz</span><b>624.0</b><small>B/frame</small></div>
          <div><span>float16+zlib xyz</span><b>176.4</b><small>B/frame</small></div>
          <div><span>ZPE packet</span><b>71.3</b><small>B/frame</small></div>
          <div><span>EmbodimentRecord</span><b>706.3</b><small>B/frame</small></div>
        </div>
        <div>
          <div><span>Segment rows</span>  <span>PASS</span></div>
          <div><span>Record overhead</span>  <span>SEPARATED</span></div>
          <div><span>Native capture</span>  <span>PENDING</span></div>
        </div>
      </div>
      <div><b>Scope:</b> synthetic OpenXR-shaped fixture, 8 segments, 96 frames. Aggregate rows are supplemental only; segment rows carry authority.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="34%" valign="top">
<div><b>06 · MEASUREMENT</b> <span>DENOMINATOR FIRST</span></div>
      <h2>No ratio without <span>a clean denominator.</span></h2>
</td>
<td width="66%" valign="top">
<div><b>06.1 · COMPARATIVE PERFORMANCE</b> <span>SYNTHETIC BYTES PER FRAME</span></div>
      <div>
        <div>
          <div><span>raw_26xyz</span>  <span>624.0 bytes/frame</span></div>
          <div><span>raw_26xyzquat</span>  <span>1456.0 bytes/frame</span></div>
          <div><span>float16+zlib xyz</span>  <span>176.4 bytes/frame</span></div>
          <div><span>ZPE packet stream</span>  <span>71.3 bytes/frame</span></div>
          <div><span>ZPE EmbodimentRecord</span>  <span>706.3 bytes/frame</span></div>
        </div>
      </div>
      <div>Packet bytes and record bytes are separated. Provenance/hash-chain overhead is separated. Orientation denominators exist when orientation exists. Adaptive-hybrid is `not_available` until prior, session, and residual bytes are separated.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07 · KEY METRICS</b> <span>MEASURED RESULTS</span></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.1 · VS RAW</b></div>
      <div>8.75<span>×</span></div>
      <div>ZPE packet stream vs raw_26xyz · <b>synthetic aggregate only</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.2 · BYTES / FRAME</b></div>
      <div>71.3<span>B</span></div>
      <div>packet stream only · <b>record bytes separate</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.3 · RECORD</b></div>
      <div>706.3<span>B</span></div>
      <div>EmbodimentRecord aggregate · <b>JSON plus stream plus provenance</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.4 · BASELINE</b></div>
      <div>176.4<span>B</span></div>
      <div>float16+zlib xyz · <b>197.5 B/frame with xyzquat</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.5 · ADAPTIVE</b></div>
      <div>n/a<span></span></div>
      <div>hybrid row withheld · <b>prior/session/residual bytes not separated</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>08 · DETERMINISM</b> <span>REPLAY AND PROVENANCE</span></div>
      <h2>Replay can be measured. Native capture <span>cannot be implied.</span></h2>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="66%" valign="top">
<div><b>08.1 · WHAT REPLAYS EXACTLY</b> <span>IN-SILICO SURFACE</span></div>
      <p>Phase 4 exercises denominator logic, record overhead, replay accounting, and provenance accounting inside a synthetic OpenXR-shaped fixture. It proves the engine can keep packets, containers, records, and hash-chain cost separate without falling back to aggregate-only reporting.</p>
      <p>The determinism claim is bounded to generated and proxy evidence. It does not prove a headset sensor path, vendor runtime parity, user-scale networking, or adaptive-hybrid compression.</p>
</td>
<td width="34%" valign="top">
<div><b>08.2 · THE AUTHORITY GAP</b></div>
      <span>Honest Blocker ·</span>
      <p><strong>Native headset capture remains pending.</strong> Surrogate and proxy records cannot satisfy native authority. CRC32 is not accepted as provenance. ContactPose remains useful history, not sovereign evidence for headset capture or enterprise deployment.</p>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="33%" valign="top">
<div><b>09</b> </div>
      <h2>WHEN MOTION BECOMES <span>A MEASURED RECORD.</span></h2>
</td>
<td width="67%" valign="top">
<div><b>09.1 · THE AMBITION</b></div>
      <p>Embodiment in XR should become durable evidence, not disposable runtime state. ZPE-XR is moving toward records that can be transported, replayed, audited, searched, and compared across headsets, engines, archives, and training pipelines. Phase 4 makes the accounting harder to fake.</p>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="33%" valign="top">
<div><b>09.2 · WHAT WORKS NOW</b></div>
        <h2>Fail-closed denominator rows, baseline comparisons, record overhead, packet overhead, provenance accounting, and synthetic replay fixtures.</h2>
</td>
<td width="67%" valign="top">
<div><b>09.3 · WHAT'S STILL OPEN</b></div>
        <h2>Native headset capture, adaptive-hybrid accounting, runtime integration, broader evidence, and release claims that survive enterprise scrutiny.</h2>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.4</b> &middot; TELEPRESENCE · NEAR-TERM (12-24 MO)</div>
      <div>Multiplayer hands need transport rows vendors can inspect</div>
      <div>The near wedge is not "smaller" alone. It is a packet stream reported beside raw, compressed, record, provenance, and replay overhead so a platform team can price bandwidth without hidden denominator swaps.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.5</b> &middot; ARCHIVES · NEAR-TERM (12-24 MO)</div>
      <div>Embodied sessions become auditable records</div>
      <div>A useful archive needs replay bytes, record bytes, and hash-chain bytes accounted separately. Phase 4 creates that accounting surface; Phase 5 must prove it against real headset capture.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.6</b> &middot; MOTION SEARCH · MID-TERM (24-48 MO)</div>
      <div>Hand motion becomes a queryable corpus</div>
      <div>Search over embodied behavior needs stable records with provenance. The current engine can generate and measure those records in silico; corpus authority waits for native capture and broader replay evidence.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.7</b> &middot; HUMAN-ROBOT REPLAY · MID-TERM (24-48 MO)</div>
      <div>Human demonstrations and robot replays share accounting</div>
      <div>A shared motion ledger is only useful if its denominators survive scrutiny. ZPE-XR can now expose packet, record, and provenance cost before pretending to bridge headset and robot motion.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.8</b> &middot; PHYSICAL AI · PARADIGM (48 MO+)</div>
      <div>Embodiment becomes measured infrastructure</div>
      <div>The long wedge is a transport and record substrate for physical behavior. The current proof is narrower: denominator-clean in-silico pressure that makes later native, adaptive, and enterprise claims harder to fake.</div>
</td>
</tr>
</table>

---

<a id="install-developer-commands-detailed"></a>

## Install / Developer Commands Detailed

<!-- INSTALL-DX:START -->
#### Package Install

Installable package: `python3.11 -m pip install zpe-xr`.
Current release: `0.3.1` on [PyPI](https://pypi.org/project/zpe-xr/).
Source: [Zer0pa/ZPE-XR](https://github.com/Zer0pa/ZPE-XR/).

```bash
python3.11 -m pip install zpe-xr
```

Import smoke:

```bash
python3.11 - <<'PY'
import importlib.metadata as md
import zpe_xr

print("zpe-xr", md.version("zpe-xr"))
PY
```

Install success only proves package acquisition/import. Product scope, PyPI state, platform limits, and blockers remain in the front-door sections above.
- Use Python 3.11 for smoke checks. Native capture and adaptive-hybrid claims remain pending.
<!-- INSTALL-DX:END -->

#### Quick Start

Install from PyPI:

```bash
pip install zpe-xr
```

Verify from source:

```bash
git clone https://github.com/Zer0pa/ZPE-XR.git zpe-xr
cd zpe-xr
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
python ./executable/verify.py
python -m pytest ./code/tests -q
```

Read `docs/ARCHITECTURE.md` first, then `docs/LEGAL_BOUNDARIES.md`, then the Phase 4 denominator artifacts. `LICENSE` is the legal source of truth; the repo uses SAL v7.1.
