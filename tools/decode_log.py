#!/usr/bin/env python3
"""
Phase 1 tool: decode a candump-format log file using the E46 PT-CAN DBC.

This does NOT need any hardware. It's here to prove the decode logic
(the DBC signal math) is correct before we ever touch an ESP32 or a car.

Usage:
    python3 decode_log.py ../sample_data/synthetic_test.log
    python3 decode_log.py path/to/your_real_candump_log.log
"""

import sys
import re
from pathlib import Path

import cantools

DBC_PATH = Path(__file__).parent.parent / "dbc" / "e46_ptcan.dbc"

# Matches a candump -l line, e.g.:
# (1725300000.100000) can0 329#460000000000FF00
LINE_RE = re.compile(
    r"^\((?P<ts>[\d.]+)\)\s+(?P<iface>\S+)\s+(?P<id>[0-9A-Fa-f]+)#(?P<data>[0-9A-Fa-f]*)$"
)


def load_log_lines(path):
    """Yield (timestamp, can_id_int, data_bytes) for each real line in a candump log."""
    with open(path, "r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank lines and our own comment lines
            m = LINE_RE.match(line)
            if not m:
                print(f"  [skip] unrecognized line format: {line}")
                continue
            ts = float(m.group("ts"))
            can_id = int(m.group("id"), 16)
            data = bytes.fromhex(m.group("data"))
            yield ts, can_id, data


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <candump_log_file>")
        sys.exit(1)

    log_path = Path(sys.argv[1])
    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        sys.exit(1)

    print(f"Loading DBC: {DBC_PATH}")
    db = cantools.database.load_file(str(DBC_PATH))
    known_ids = {msg.frame_id: msg for msg in db.messages}
    print(f"  {len(known_ids)} message IDs known: "
          f"{', '.join(f'0x{i:X}' for i in sorted(known_ids))}")
    print()

    print(f"Decoding {log_path} ...")
    print("-" * 70)

    seen_unknown_ids = set()
    decoded_count = 0

    for ts, can_id, data in load_log_lines(log_path):
        msg = known_ids.get(can_id)
        if msg is None:
            # Not an error - the bus carries tons of IDs we haven't decoded yet.
            seen_unknown_ids.add(can_id)
            continue

        if not msg.signals:
            # We know this ID exists (e.g. 0x545 warning lights) but haven't
            # mapped its bits yet - say so instead of pretending we decoded it.
            print(f"[{ts:.3f}] 0x{can_id:03X} {msg.name:22s} "
                  f"(known ID, signals NOT mapped yet - raw: {data.hex()})")
            continue

        try:
            decoded = db.decode_message(can_id, data)
        except Exception as e:
            print(f"[{ts:.3f}] 0x{can_id:03X} {msg.name:22s} DECODE ERROR: {e}")
            continue

        decoded_count += 1
        values = ", ".join(f"{k}={v}" for k, v in decoded.items())
        print(f"[{ts:.3f}] 0x{can_id:03X} {msg.name:22s} {values}")

    print("-" * 70)
    print(f"Done. {decoded_count} messages fully decoded.")
    if seen_unknown_ids:
        ids_str = ", ".join(f"0x{i:X}" for i in sorted(seen_unknown_ids))
        print(f"Saw {len(seen_unknown_ids)} CAN ID(s) not in our DBC yet: {ids_str}")
        print("(Expected - the real bus carries many more IDs than we've decoded.)")


if __name__ == "__main__":
    main()
