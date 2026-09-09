# Decisions log
One line per decision. Newest at the bottom. This is how we avoid re-arguing settled things.

- 2026-xx: Tap PT-CAN at DME X6004 pins 36/37, not OBD-II (OBD-II on E46 is K-line only).
- 2026-xx: Hardware = ESP32 (TWAI) + SN65HVD230 (3.3V). Listen-only, no termination resistor.
- 2026-xx: Dev flow = PC validation → USB-CAN bench → ESP32 firmware → display → car.
- 2026-xx: macOS is primary dev machine; SocketCAN unavailable, so use python-can slcan.
- 2026-09-08: Repo structure + CLAUDE.md created. Git is the source of truth for code; cloud-sync folders are NOT used for the repo.
