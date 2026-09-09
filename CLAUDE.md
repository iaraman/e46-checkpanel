# CLAUDE.md — project brain (read at the start of every session)

## What this project is
Retrofit "check control" instrument/diagnostic module for the BMW E46 chassis,
styled after the E30 panel, mounted in the roof console (sunroof switch location).
Passively reads PT-CAN for live values, actively reads fault codes/live data from
DME and DSC over K-line, and reads a retrofitted oil pressure sender. Personal
learning project first; sellable product is a possible later outcome.

**Full spec, scope, and requirements: `docs/REQ-001-requirements.md`.** Read it
before proposing anything that touches scope — this file is a summary, not the
source of truth.

## Who I'm working with
Ian is new to software development. Explain what you're doing and why as you go —
don't assume he knows standard tooling conventions (git, venvs, package managers,
etc.). I (Claude) write all the code. Ask before big design or scope changes.

## Current phase
Phase 1 (Python decode + synthetic log) is done. Phase 2 (bench test with a
USB-CAN adapter via python-can) is next. See `docs/REQ-001-requirements.md` §9
for the full verification plan (V1–V11) and where we are on it.

## Tech stack
- **PC-side tools:** Python 3.12, in a `.venv` (see `scripts/setup-mac.sh` /
  `setup-windows.ps1`). Key libs: `cantools`, `python-can`, `pyserial`.
- **Firmware (not started — Phase 3):** ESP32-S3 (native USB, PSRAM), PlatformIO,
  TWAI driver for CAN, SN65HVD230 transceiver. K-line via ISO 9141 transceivers.
- **Editor:** VS Code, with recommended extensions in `.vscode/extensions.json`.
- Cross-platform by requirement — nothing macOS-only or Windows-only.

## Directory layout — what belongs where
| Folder | What lives here |
|---|---|
| `docs/` | Requirements, decisions, CAN map, learning log (human-readable knowledge) |
| `docs/reference/` | Raw evidence captures (INPA sessions, datasheets) — append-only, don't edit |
| `tools/` | Python scripts that run on your computer (decode logs, bench testing) |
| `sample_data/` | CAN logs — synthetic now, real captures later |
| `firmware/` | ESP32 code (PlatformIO project) — **empty until Phase 2 bench testing is done** |
| `scripts/` | One-shot setup scripts for macOS and Windows |
| `.venv/` | Python virtual environment — gitignored, don't commit it |

## Hard facts (do not re-derive, they cost Ian time and money)
- PT-CAN tap: DME connector X6004 pins 36/37 under dash. NOT the OBD-II port.
- PT-CAN: listen-only, no ACK, **no transmit in v1/v2** (safety requirement, see
  REQ-001 §6 SF-01). No termination resistor — bus is already terminated.
- K-line #1 = OBD-II pin 7 (DME, EGS). K-line #2 = OBD-II pin 8 (DSC, SRS, IKE,
  LCM) — confirmed working via INPA.
- Diagnostics are **read-only** in v1: no clear/write/coding code path, enforced
  at build time (REQ-001 §6 SF-02).
- Signal decode formulas and confidence ratings: `docs/REQ-001-requirements.md` §8.
  `docs/CAN_MAP.md` is older and less complete — prefer REQ-001 where they differ.

## House rules
- Python for PC-side tools, C++ (Arduino/ESP-IDF via PlatformIO) for firmware.
- Small commits, clear messages. Never commit secrets or build output (`.venv/`,
  `.pio/`, `build/` are gitignored).
- Keep responses short; Ian is on a budget. Don't restate the plan every turn.
- When a decision is made, append one line (dated) to `docs/DECISIONS.md`.
- Ian keeps his own notes in `docs/LEARNING_LOG.md` — don't write to it for him.
