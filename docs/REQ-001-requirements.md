# E46 Check Panel — Development Requirements Sheet

**Document:** REQ-001
**Revision:** v0.3 (DRAFT)
**Date:** 2026-09-09
**Owner:** Ian
**Status:** Open for revision. Sections marked ⚠ contain unverified assumptions.

---

## 1. Product Definition & Scope

### 1.1 Product summary

A retrofit instrument and diagnostic module for the BMW E46 chassis, mounted in the
roof console in place of the sunroof switch panel, and styled to be visually
indistinguishable from factory-era BMW instrumentation. The device passively monitors
the PT-CAN powertrain bus for live vehicle data, actively queries vehicle control
modules over K-line for stored fault codes and live values, and reads a retrofitted
analog oil pressure sender. It presents this data on an amber monochrome display
behind a custom bezel that also re-houses the displaced sunroof switches.

**Project intent:** personal build, undertaken primarily as a learning exercise.
Commercial productisation is a possible long-term outcome but is not a v1 driver.
Requirements existing only to serve a hypothetical product are marked *(product-only)*.

**Capability benchmark:** the target is INPA-equivalent read capability for the
modules in scope — not a superset, and not a generic OBD-II scanner.

### 1.2 In scope for v1

| Ref | Item |
|-----|------|
| SC-01 | Live value display sourced from PT-CAN (passive listen) |
| SC-02 | Oil pressure measurement via retrofitted analog sender |
| SC-03 | Fault code **reading** from all reachable modules over both K-lines |
| SC-04 | Live-data **reading** from modules over K-line (values not present on PT-CAN) |
| SC-05 | Threshold-based warning alerts with era-appropriate symbology |
| SC-06 | MS43 (Siemens MS 43.0 / M54) as the primary and only validated DME variant |
| SC-07 | Non-destructive installation — no cut factory wiring, reversible in under 1 hour |
| SC-08 | Sunroof switch function preserved and re-housed in the new bezel |

**Market scope:** US / North American E46 variants only. Petrol M54 only. Diesel,
318, 320 and other non-NA variants are permanently out of scope.

### 1.3 Deferred scope

| Ref | Item | Target |
|-----|------|--------|
| OS-01 | Clearing / resetting fault memory | v2 |
| OS-02 | USB diagnostic bridge mode (laptop talks to car through the unit) | v2 |
| OS-03 | Data logging to removable media | v2 |
| OS-04 | Wireless connectivity (BT/WiFi) | v2 |
| OS-05 | MS45 DME support | v2 |
| OS-06 | DSC 5.7 support (xDrive cars) | v1.1 |
| OS-07 | Module coding, adaptation reset, or flashing | v3 |
| OS-08 | Transmission on PT-CAN | v3 — see SF-01 |
| OS-09 | Non-E46 chassis support | v3 |

> **Note on OS-01.** The v1 firmware shall contain no code path capable of emitting a
> write, clear, or coding request. Enforced at build time, not at runtime.
>
> **Note on OS-08.** Moving from a passive to an active node on PT-CAN is a change of
> risk class, not a feature addition. PT-CAN arbitrates engine, braking and
> transmission traffic. Lifting SF-01 requires a dedicated safety review.

---

## 2. Vehicle Compatibility Matrix

**Primary development target:** 2002 E46 325iT (Touring), M54, Siemens MS43, manual.

| Car | Year | DME | Trans | Drive | DSC | Role |
|-----|------|-----|-------|-------|-----|------|
| 325iT | 2002 | MS43 (`MS430DS0`) | Manual | RWD | MK60 ⚠ | **Primary target** |
| 325i | ~2003 ⚠ | MS43 | Manual | RWD | MK60 ⚠ | Secondary MS43 validation |
| 325xi | ~2002 ⚠ | MS43 (`MS430DS0`) | Auto | AWD | **DSC57 — confirmed** | EGS + DSC 5.7 coverage |
| 325i | 2005 | MS45 | Manual | RWD | MK60 ⚠ | v2 MS45 target |

**Confirmed by INPA session evidence (09/08–09/09/26):**

- DME variant string is `MS430DS0` on both the 325iT and the 325xi — a single DME
  target covers three of the four cars.
- The 325xi reports `ECU: DSC57, Variant: DSC57`. INPA's E46 chassis script list
  presents `DSC MK60` and `DSC 5.7` as **separate scripts**, confirming two distinct
  SGBDs with distinct job sets and distinct record formats.
- DSC error records contain no raw `Errorcode:` field, no logistic counter, and a
  different environmental payload (vehicle speed plus named system-state booleans).
  **DSC and DME require separate record parsers.**
- Other E46 chassis-group modules visible in INPA: steering angle sensor, tire
  pressure control, deflation warning system.

| Attribute | Target | Notes |
|-----------|--------|-------|
| PT-CAN | 500 kbit/s, 11-bit standard IDs | Confirmed |
| K-line #1 (TxD) | OBD-II socket pin 7 | DME, EGS |
| K-line #2 (TxD2) | OBD-II socket pin 8 | DSC, SRS, IKE, LCM. Presence confirmed — DSC read successfully through the OBD-II port |
| K-bus | Body network; SHD, IKE, LCM, MRS, LSZ, GM5, RLS et al. | Present in the roof harness at the sunroof switch (white/red/yellow) ⚠. **DSC is not a K-bus module** |

**CM-01:** The device shall detect at startup which modules respond and shall not
display or alert on values sourced from absent modules (e.g. EGS on manual cars).

**CM-02:** DME and DSC variants shall be identified at runtime rather than compiled
in, so a single firmware image serves the whole fleet.

**CM-03:** MK60 is the priority DSC target (three of four cars). DSC 5.7 follows at v1.1.

---

## 3. Functional Requirements

### 3.1 Live value display (PT-CAN, passive)

| Ref | Requirement | Source | Priority |
|-----|-------------|--------|----------|
| FR-01 | Display coolant temperature in °C, 1° resolution | CAN 0x329 B1 | Must |
| FR-02 | Display engine oil temperature in °C, 1° resolution | CAN 0x545 B4 | Must |
| FR-03 | Display engine speed (RPM) | CAN 0x316 B2–B3 | Should |
| FR-04 | Display throttle position, 0–100% | CAN 0x329 B5 | Could |
| FR-05 | Display transmission oil temperature and selected gear (EGS cars only) | CAN 0x43F ⚠ | Should |
| FR-06 | Display instantaneous and trip-average fuel consumption | CAN 0x545 B1–B2 delta | Could |
| FR-07 | Display individual wheel speeds | ASC on CAN (primary) / DSC DS2 (fallback) | **Must** |
| FR-08 | Display brake line pressure | CAN 0x1F8 B2 ⚠ | Could |

**FR-09:** All CAN-sourced values shall be marked stale and visually indicated as such
if the source message has not been received within 3× its nominal period.

> **FR-07 method.** Resolve the CAN decode by correlation: log PT-CAN while INPA
> displays DSC live wheel speeds on a moving car, then solve the byte stream against
> timestamped ground truth. Ship the CAN path — passive, continuous, no bus load.
> Retain the DS2 job as documented fallback. If the ASC broadcast proves to carry only
> a filtered or derived speed rather than four sensors, FR-07 reverts to the K-line
> path and acquires an explicit refresh-rate requirement.

### 3.2 Analog inputs

| Ref | Requirement | Priority |
|-----|-------------|----------|
| FR-10 | Display engine oil pressure in psi from retrofitted sender, resolution ≤1 psi | Must |
| FR-11 | Display system/charging voltage, resolution 0.1 V | Must |
| FR-12 | Oil pressure channel shall support a user-entered two-point calibration | Should |
| FR-13 | The factory low-pressure switch shall remain functional after sender installation | Must |

### 3.3 Diagnostics (K-line, read-only in v1)

| Ref | Requirement | Priority |
|-----|-------------|----------|
| FR-14 | Read stored fault memory from the DME over K-line #1 | Must |
| FR-15 | Read stored fault memory from DSC over K-line #2 (DS2, 9600 baud, address 0x56) | Must |
| FR-16 | Read stored fault memory from EGS, SRS, IKE, LCM where present | Should |
| FR-17 | Display fault number, plain-language description, status flags and error frequency | Must |
| FR-18 | Decode and display environmental/freeze-frame values for recognised fault codes; display raw bytes with generic labels for unrecognised ones | Must |
| FR-19 | Read module live-data values not available on PT-CAN | Should |
| FR-20 | Support generic OBD-II mode $03 as a fallback path | Could |
| FR-21 | Diagnostic sessions shall be user-initiated, not continuously polling in the background | Must |

> **FR-18 scoping.** The fault-number→text table and the per-fault environmental
> variable mapping both live in the SGBD and cannot be derived from record bytes
> alone. Build the table incrementally from faults actually encountered across the
> four-car fleet rather than attempting to transcribe the SGBD up front. Graceful
> degradation to raw bytes is what makes this strategy viable.

### 3.4 Alerts

| Ref | Requirement | Priority |
|-----|-------------|----------|
| FR-22 | Raise a visual alert when any monitored value crosses a configured threshold | Must |
| FR-23 | Alerts shall use era-appropriate symbology (E30 check-control visual language) | Must |
| FR-24 | Mirror the DME's own warning bits: check engine, EML, overheat, oil level, charge | Should |
| FR-25 | Alerts shall latch until acknowledged, and record time-since-first-trigger | Should |
| FR-26 | Thresholds shall be user-configurable, with sane compiled-in defaults | Should |
| FR-27 | Latched alerts and session min/max values shall persist across ignition cycles | Should |
| FR-28 | No audible alert element in v1 | — |

**Default thresholds (provisional — validate against real operating data):**

| Value | Caution | Critical |
|-------|---------|----------|
| Coolant temp | 110 °C | 118 °C |
| Oil temp | 125 °C | 140 °C |
| Oil pressure (>2000 RPM) | <15 psi | <8 psi |
| System voltage | <12.8 V or >14.9 V | <11.8 V or >15.5 V |

### 3.5 User interface

| Ref | Requirement | Priority |
|-----|-------------|----------|
| FR-29 | Input via physical buttons integrated into the bezel | Must |
| FR-30 | Button feel, travel and finish shall be consistent with E46 interior switchgear | Should |
| FR-31 | Sunroof switches shall be re-housed in the bezel and retain full factory function. **Note:** the switch signals are coded ground combinations across three wires, not simple contacts — the coding must be preserved intact | Must |
| FR-32 | Primary live-value screen shall be reachable from any state with a single button press | Should |

---

## 4. Non-Functional Requirements

### 4.1 General

| Ref | Requirement | Rationale |
|-----|-------------|-----------|
| NFR-01 | Valid data displayed within 2.0 s of terminal 15 | Must feel factory-integrated |
| NFR-02 | Live values refresh at ≥10 Hz; displayed numerics may be damped | |
| NFR-03 | Operating temperature range −30 °C to +85 °C | Roof console; direct solar gain through the sunroof aperture |
| NFR-04 | Quiescent current with terminal 15 off <1 mA | |
| NFR-05 | Survive 9–16 V continuous and ISO 7637-2 transients | |
| NFR-06 | Independent hardware watchdog | |
| NFR-07 | Firmware field-updatable without removing the unit | Roof access is awkward |
| NFR-08 | Legible in direct sunlight; dims with instrument illumination | |

### 4.2 Extensibility — *no-overhaul requirements*

| Ref | Requirement | Protects |
|-----|-------------|----------|
| NFR-09 | Target ≤50% flash and ≤50% RAM utilisation at v1 feature-complete | v2/v3 headroom |
| NFR-10 | Display shall be **dot-matrix monochrome**, not fixed-segment glass | Arbitrary text, menus, future layouts |
| NFR-11 | CAN transceiver footprint and MCU configuration shall physically support transmit, gated in firmware only | OS-08 without a respin |
| NFR-12 | ≥4 spare MCU GPIO, one spare I²C address range, ≥20% spare pins on every external connector | Sensors, storage, radio |
| NFR-13 | Vehicle interface shall be a hardware abstraction layer; application logic shall not call CAN or UART primitives directly | Chassis/DME portability |
| NFR-14 | Signal decodes, fault-code tables and environmental variable maps shall be **data**, loaded from structured files, not hard-coded logic | New variants become a data update |
| NFR-15 | The diagnostic layer shall abstract at **two** levels: transport (DS2 / KWP2000 / OBD-II) *and* record format (per module family). DSC and DME records are structurally different and require separate parsers | Module additions |
| NFR-16 | Enclosure and bezel shall permit display module replacement without redesigning the mounting | Panel obsolescence |

### 4.3 Platform decision

**Selected MCU: ESP32-S3** (WROOM-1 class module, ≥8 MB flash, PSRAM optional-but-fitted).

Rationale:

- **Native USB** — enables firmware update without a serial adapter, and enables OS-02
  (USB diagnostic bridge). This is the deciding factor; the original ESP32 cannot do it.
- **PSRAM headroom** — removes the entire class of memory-exhaustion risk against NFR-09.
- **TWAI present** — the CAN design carries over unchanged.
- **Current silicon** — longer support horizon than the 2016-vintage ESP32.

⚠ **Open risk:** most ESP32-S3 modules are rated −40 to +85 °C, placing NFR-03 at the
limit rather than inside it. Roof-console ambient under summer solar load is close to
worst case. Mitigation options: accept derating risk on a personal build, specify an
industrial-grade module, or design enclosure venting. To be resolved before PCB layout.

---

## 5. Interface Requirements

### 5.1 PT-CAN

| Ref | Requirement |
|-----|-------------|
| IF-01 | ESP32-S3 TWAI controller + SN65HVD230 (3.3 V) transceiver |
| IF-02 | Configured **listen-only / TWAI_MODE_NO_ACK** in v1/v2; no ACK, no transmitted frame |
| IF-03 | No 120 Ω termination resistor — passive tap on an already-terminated bus |
| IF-04 | Tap at DME connector X6004 pins 36/37 (CAN+/CAN−) |

### 5.2 K-line

| Ref | Requirement |
|-----|-------------|
| IF-05 | Two independent K-line channels via 12 V bidirectional ISO 9141 transceivers (L9637D or equivalent) |
| IF-06 | Channel A → OBD-II pin 7 (DME, EGS) |
| IF-07 | Channel B → OBD-II pin 8 (DSC, SRS, IKE, LCM) — confirmed present on the target car |
| IF-08 | Channels shall remain electrically separable and shall not be hard-bridged |
| IF-09 | Transceivers held high-impedance/idle whenever no diagnostic session is active |

### 5.3 Analog & power

| Ref | Requirement |
|-----|-------------|
| IF-10 | Oil pressure sender: ratiometric 0.5–4.5 V, 0–150 psi. Port thread is **M12×1.5** (factory switch location). Installation shall use a tee or adapter that retains the factory switch (FR-13) |
| IF-11 | Analog acquisition via external I²C ADC (e.g. ADS1115), not the ESP32 internal ADC |
| IF-12 | Battery voltage divider with input filtering and transient clamping |
| IF-13 | Power from terminal 15 only. **No terminal 30.** FR-27 persistence achieved by ignition-off edge detection plus flash write, with a hold-up capacitor sized to guarantee completion |
| IF-14 | Illumination dimming input from the instrument light circuit (PWM sense) |

### 5.4 Harness

| Ref | Requirement |
|-----|-------------|
| IF-15 | Roof-console location requires a routed run to the under-dash tap points, likely via the A-pillar. Designed, sleeved, connectorised assembly with service loops |
| IF-16 | CAN pair twisted for the full run; K-line and analog runs separated from the CAN pair where practical |
| IF-17 | A single vehicle-side connector at the unit, permitting removal without disturbing the harness |
| IF-18 | The roof K-bus tap is a possible harness simplification but **shall not be a design assumption** — DSC is not reachable over K-bus, and the electrical relationship between OBD pin 8 and the roof K-bus is unverified ⚠ |

---

## 6. Safety & Fail-Safe Requirements

| Ref | Requirement |
|-----|-------------|
| SF-01 | **v1 and v2:** the device shall not transmit on PT-CAN. Enforced by hardware mode configuration, verified at release sign-off. Any future change (OS-08) requires an independent safety review |
| SF-02 | The v1 firmware shall implement only read-class diagnostic services. No clear, write, coding, or flash service compiled into the binary |
| SF-03 | Read-class operations — fault memory reads and live-data polling — permitted at any road speed. **Write-class operations, when introduced in v2, permitted only with the vehicle stationary and with explicit user confirmation** |
| SF-04 | Any fault, hang, or watchdog reset shall have no effect on vehicle operation. The device is a leaf node with no authority |
| SF-05 | The device shall never present itself as a required module or respond to any bus address |
| SF-06 | On loss of a data source, display an explicit "no data" state rather than a stale or zeroed value |
| SF-07 | Diagnostic sessions shall time out and release both K-lines after a bounded period of no user interaction |
| SF-08 | Displayed values are advisory. The device does not replace factory instrumentation or a service-grade tool |

---

## 7. Aesthetic & Mechanical Requirements

| Ref | Requirement |
|-----|-------------|
| AM-01 | Amber/orange monochrome, matched empirically to the car's instrument illumination hue (~605–615 nm nominal ⚠) |
| AM-02 | Primary numeric readout in a segment-style typeface rendered without anti-aliasing |
| AM-03 | Smoked/tinted front window so unlit areas read as dead black |
| AM-04 | 3D-printable bezel masking all non-active display area, re-housing the sunroof switches, matching E46 trim in finish, radius language and colour |
| AM-05 | A short boot logo or animation is permitted, provided it reads as period-correct — segment-style or simple amber motif. No modern branding, gradients, or colour |
| AM-06 | Oil pressure presented as a **digital numeric readout in psi** (e.g. `25 PSI`) in the amber segment typeface. Analog character comes from the display treatment and physical buttons, not simulated instruments |
| AM-07 | Diagnostic/text mode may relax AM-02 but shall remain within the monochrome amber palette |
| AM-08 | No permanent modification to visible interior trim |
| AM-09 | Where console depth is insufficient, a modest tilt or protrusion is acceptable if it reads as deliberate and does not foul the sunroof, headliner, or head clearance |
| AM-10 | OLED vs transflective FSTN LCD decided by side-by-side prototype, weighing contrast and glow authenticity against burn-in resistance and sunlight legibility |

---

## 8. Signal Reference & Confidence Register

### 8.1 PT-CAN signals

| Signal | Source | Decode | Conf. |
|--------|--------|--------|-------|
| Engine speed | 0x316 B2–B3 (LE) | RPM = raw × 0.1558 | A |
| Coolant temp | 0x329 B1 | °C = 0.75 × raw − 48.373 | A |
| Throttle position | 0x329 B5 | 0x00–0xFE → 0–100% | B |
| Oil temperature | 0x545 B4 | °C = raw − 48.373 | B |
| Check engine lamp | 0x545 B0 bit 1 | boolean | B |
| Cruise lamp | 0x545 B0 bit 3 | boolean | B |
| EML lamp | 0x545 B0 bit 4 | boolean | B |
| Gas cap lamp (2002+) | 0x545 B0 bit 7 | boolean | C |
| Oil level warning / error | 0x545 B3 bits 1, 2 | boolean | C |
| Overheat lamp | 0x545 B3 bit 3 | boolean | B |
| Charge lamp | 0x545 B5 | boolean, DME-dependent | C |
| Fuel consumption | 0x545 B1–B2 | rolling counter, rate of change | B |
| Odometer | 0x613 | ×10 = km | C |
| Fuel level | 0x613 B2 | nonlinear, wraps above 0x80 | C |
| Brake pressure | 0x1F8 B2 | scale unknown | C |
| ASC/DSC error lamp | 0x153 | one confirmed bit | C |
| Wheel speeds | ASC messages | ID and layout unconfirmed | C |
| EGS gear / trans oil temp | 0x43F | byte layout unconfirmed | C |
| Oil pressure | **Not on CAN** | Requires retrofitted sender | A |
| Battery voltage | **Not on CAN** | Requires analog divider | A |

### 8.2 MS43 DS2 error record format — **CONFIRMED (rated A)**

Derived from 16 records across two cars (325iT 09/08/26, 325xi 09/09/26) by
cross-referencing INPA's `Errorcode:` raw bytes against its own decoded output.
Every field reconciles on every record.

**Record: 10 bytes.**

| Byte | Field |
|------|-------|
| 0 | Fault number (decimal) |
| 1 | Status bitfield (below) |
| 2 | Error frequency |
| 3 | Logistic counter |
| 4–7 | Four environmental values, fault-code-specific |
| 8–9 | Operating-hours snapshot, **big-endian uint16, 0.1 h/LSB** |

**Byte 1 bitfield:**

| Bit | Meaning |
|-----|---------|
| 7 | Error relevant |
| 6 | Error currently present |
| 5 | Error debounce |
| 4 | Sporadic (0 = static) |
| 3–0 | Four fault-specific condition flags, mapping in order to INPA's four condition slots |

**Age calculation:** INPA reports `aufgetreten vor (rel. BZ)` — occurred before,
relative to operating time — as `(current_counter − stored_counter) × 0.1 h`. The
current counter must be read separately from the DME. Reconciled values at capture:
325iT = 4796.9 h (`0xBB61`), 325xi = 2735.4 h (`0x6ADA`).

**Environmental value scalings — all confirmed to displayed precision:**

| Variable | Formula |
|----------|---------|
| `TCO` | °C = 0.75 × raw − 48 |
| `N_32`, `N_32_TOL` | rpm = raw × 32 |
| `MAF`, `MAF_TOL`, `MAF_BOL` | mg/stk = raw × 5.4471 |
| `VB`, `V_IGK` | V = raw × 0.102 |
| `LAM_MV_1`, `LAM_MV_2` | % = (raw − 128) × 100/256 |
| `ISAPWM` | % = raw × 100/255 |
| `THR` | °TPS = raw × 0.78125 |
| `GEAR_SEL_DISP` | raw, unscaled |

**Not derivable from record bytes** — both live in the SGBD and must be captured or
built incrementally: the fault-number→text table, and the per-fault mapping of which
four variables occupy bytes 4–7. Observed examples: fault 37 → `{VB, V_IGK, TCO,
N_32}`; fault 227 → `{N_32, MAF, TCO, LAM_MV_1}`; fault 239 → `{TCO, N_32_TOL,
MAF_TOL, MAF_BOL}`.

### 8.3 DSC57 record format

Structurally different from the DME record: **no raw `Errorcode:` field**, no logistic
counter, error frequency saturates at 255, and the environmental payload is a vehicle
speed plus named system-state booleans (ASC/ABS/HBA/ECD/HDC active-passive, stop light
switch). Requires its own parser. Rated **C** — no raw bytes captured yet.

MK60 format unknown and separately rated **C**.

### 8.4 Sources

- **PT-CAN:** MS4X wiki MS43 CAN bus message table (ECU firmware analysis) in
  preference to forum posts. Rebuild `e46_ptcan.dbc` against it.
- **K-line:** EDIABAS interface trace. Enable tracing in `EDIABAS.INI` ⚠ (exact keys
  TBC), execute the target job in Tool32, read raw request/response bytes from the log.
- **Fault tables:** incremental capture across the four-car fleet.

---

## 9. Verification & Test Plan

| Phase | Gate criteria |
|-------|---------------|
| V1 — Desk decode | Every signal in §8.1 decodes correctly from synthetic frames (complete) |
| V2 — Bench CAN | PC + USB-CAN replays a real captured drive log; values plausible and continuous |
| V3 — K-line capture | EDIABAS traces captured for every job in scope; request/response framing documented |
| V4 — Record parser | §8.2 parser validated against all 16 known records plus newly captured ones |
| V5 — Bench K-line | ESP32-S3 reproduces captured exchanges against a real module; logic analyser capture archived |
| V6 — Wheel speed correlation | PT-CAN log correlated against INPA DSC live data on a moving car; FR-07 decode resolved or fallback invoked |
| V7 — Ground truth | Every displayed value cross-checked against INPA/Tool32, same car, same session. Deviations >2% investigated |
| V8 — Analog cal | Oil pressure verified against a mechanical gauge teed into the same port across full range; factory switch confirmed still functional |
| V9 — Environmental | Soaked at 85 °C and −20 °C; quiescent current measured after 24 h |
| V10 — Fleet compatibility | Single firmware image verified on all four cars; absent-module handling confirmed |
| V11 — In-car | 500 km mixed driving, no bus errors, no spurious alerts, no interference |

---

## 10. Open Questions & Research Spikes

### Resolved

| # | Question | Resolution |
|---|----------|------------|
| Q1 | K-line #2 access path | OBD-II pin 8, confirmed by successful INPA DSC access |
| Q3 | K-line bridging | Not required. The cable switch is most likely a K-line/D-CAN protocol selector for later chassis, not a 7↔8 bridge ⚠ |
| Q5 | Mounting location | Roof console, sunroof switch panel |
| Q6 | Display technology | Monochrome dot-matrix, segment-style rendering. OLED vs FSTN open (AM-10) |
| Q7 | Fault description licensing | Deferred — personal project |
| Q8 | Audible alerts | No |
| Q9 | Terminal 30 | Not required |
| Q10 | Input method | Physical buttons in the bezel |
| Q13 | Oil pressure port | M12×1.5, factory switch location. Tee required to retain the switch |
| Q16 | MCU | ESP32-S3 — see §4.3. Thermal rating remains an open risk |
| Q17 | Capability scope | INPA-equivalent read capability, US/NA petrol M54 variants only |
| Q18 | DSC variants | Confirmed distinct. `DSC57` on the xi; MK60 a separate INPA script. Separate parsers required |
| Q19 | Wheel speed approach | CAN primary, resolved by correlation against INPA DSC live data; DS2 job retained as fallback |
| — | MS43 error record format | **Solved.** See §8.2 |

### Open

| # | Question | Blocks |
|---|----------|--------|
| Q12 | Exact `EDIABAS.INI` trace configuration keys on the local install | V3 |
| Q14 | Is the roof K-bus electrically the same net as OBD pin 8? Continuity check | IF-18 |
| Q15 | Available depth behind the sunroof switch panel; headliner and cassette clearance | AM-09, enclosure |
| Q20 | ESP32-S3 module thermal rating vs. NFR-03 — accept, upgrade, or vent? | PCB layout, enclosure |
| Q21 | DS2 request framing: how is the error memory read job addressed and structured per module? | FR-14–FR-16 |
| Q22 | How is the DME's current operating-hours counter read? Required for §8.2 age calculation | FR-18 |
| Q23 | Which DS2 live-data jobs are needed per module, and at what refresh rate? | FR-19, FR-07 fallback |
| Q24 | MK60 error record format — capture raw bytes from an MK60 car | 8.3, CM-03 |
| Q25 | Does the ASC broadcast carry four individual wheel speeds or a single derived value? | FR-07 |

---

## Revision History

| Rev | Date | Change |
|-----|------|--------|
| v0.1 | 2026-09-09 | Initial draft. Read-only diagnostics, retrofitted oil pressure sender, MS43 primary target |
| v0.2 | 2026-09-09 | K-line #2 confirmed at OBD-II pin 8; test fleet matrix; extensibility requirements; SF-01 versioned, SF-03 relaxed for read-class; roof console location; dot-matrix display fixed; EDIABAS trace method adopted |
| v0.3 | 2026-09-09 | **MS43 DS2 error record format decoded and rated A (§8.2)** from INPA session evidence. MCU decision: ESP32-S3 (§4.3) with thermal risk flagged. DSC57 vs MK60 confirmed as separate targets; NFR-15 deepened to require per-module record parsers. Market scope narrowed to US/NA petrol M54. FR-13 added to retain factory oil pressure switch. FR-31 amended for three-wire coded sunroof switch signals. Q19 wheel-speed strategy resolved as CAN-primary via correlation. USB bridge mode added as OS-02 |
