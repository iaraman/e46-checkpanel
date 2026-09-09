# Reference Material

Primary-source captures taken from the project's own vehicles. These are **evidence**,
not documentation — every decode claim rated **A** or **B** in `REQ-001-requirements.md`
§8 traces back to something in this folder.

Do not edit these files. If a capture is superseded, add the new one alongside it and
note the reason here.

## `inpa/` — BMW INPA sessions

Captured with INPA 5.00 (E46 script set V1.30) over a K+DCAN cable through the OBD-II
port, on a Windows laptop.

| File | Car | ECU | Date | Contents |
|------|-----|-----|------|----------|
| `2026-09-08_325iT_MS430DS0_fault-memory.pdf` | 2002 325iT (primary target) | MS43 DME | 08 Sep 2026 | 9 faults, each with raw `Errorcode:` bytes |
| `2026-09-09_325xi_MS430DS0_fault-memory.pdf` | 325xi | MS43 DME | 09 Sep 2026 | 7 faults, each with raw `Errorcode:` bytes |
| `2026-09-09_325xi_DSC57_fault-memory.pdf` | 325xi | DSC 5.7 | 09 Sep 2026 | 3 faults, no raw bytes |
| `2026-09-09_inpa-e46-chassis-script-list.png` | — | — | 09 Sep 2026 | INPA script selection dialog, E46 chassis group |

### Why these matter

**The two MS43 reports are the source of the §8.2 record decode.** INPA prints the raw
10-byte fault record on the `Errorcode:` line *alongside* its own decoded rendering of
the same bytes. That pairing is what allowed the format to be solved without a protocol
trace — 16 records, every field reconciling on every record.

Derived and confirmed from these two files:

- 10-byte record layout (fault number, status bitfield, frequency, logistic counter,
  four environmental bytes, operating-hours snapshot)
- Byte 1 status bit meanings, including the four fault-specific condition flags
- Environmental scalings for `TCO`, `N_32`, `MAF`, `VB`, `LAM_MV_x`, `ISAPWM`, `THR`
- The age-calculation method, and the operating-hours counter value at each capture
  (325iT = 4796.9 h, 325xi = 2735.4 h)

**The DSC57 report is the source of the §8.3 finding** that DSC and DME records are
structurally different — no raw `Errorcode:` field, no logistic counter, frequency
saturating at 255, and a different environmental payload. This is why the diagnostic
layer needs per-module record parsers rather than a single one.

**The script list screenshot confirms** `DSC MK60` and `DSC 5.7` are separate INPA
scripts, i.e. separate SGBDs — the basis for treating MK60 and DSC 5.7 as two
implementation targets (CM-03). It also inventories the other E46 chassis-group modules
reachable over K-line #2: steering angle sensor, tire pressure control, deflation
warning system.

### Known gaps

- No raw bytes for any DSC record, MK60 or 5.7 — blocks Q24
- No EDIABAS interface trace yet, so the **request** framing is still unknown — blocks
  Q21 and Q22
- No MS45 capture (2005 325i) — needed before OS-05

### Adding to this folder

When capturing new material, keep the naming convention
`YYYY-MM-DD_<car>_<ECU>_<what>.<ext>` and add a row to the table above with a one-line
note on what it establishes. A capture nobody can interpret in six months is not
evidence.
