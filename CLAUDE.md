# CLAUDE.md — project brain (Claude Code reads this at the start of every session)

## What this project is
Retrofit "check control" panel for the BMW E46, styled after the E30 panel.
ESP32 passively listens to PT-CAN (500 kbps, 11-bit IDs) and shows RPM, coolant temp,
voltage, and warning lights on a small display. Goal: sellable product.

## Who I'm working with
Ian has no coding background. He installs tools, runs commands, reports results, and
directs the project. I write ALL code. Explain in plain language, anchored to real files
in this repo. Say when I'm unsure. Ask before big design changes.

## Phases (check docs/DECISIONS.md before changing course)
1. DONE  — Python decode script + synthetic log (tools/, sample_data/)
2. NEXT  — Bench test with USB-CAN adapter via python-can (slcan)
3.       — ESP32 firmware (PlatformIO, TWAI driver, SN65HVD230 transceiver)
4.       — Display layer (mock visuals in chat first, then LVGL)
5.       — In-car validation

## Hard facts (do not re-derive these, they cost Ian time and money)
- PT-CAN tap: DME connector X6004 pins 36/37 under dash. NOT the OBD-II port (that's K-line).
- Listen-only mode. NO termination resistor (bus already terminated).
- See docs/CAN_MAP.md for message IDs and decode formulas. DBC lives in tools/e46_ptcan.dbc.

## House rules
- Python for PC-side tools, C++ (Arduino/ESP-IDF via PlatformIO) for firmware.
- Small commits with clear messages. Never commit secrets or build output.
- Keep responses short; Ian is on a budget. Don't restate the plan every turn.
- When a decision is made, append it to docs/DECISIONS.md with the date.
- Cross-platform: nothing that only works on macOS or only on Windows.
