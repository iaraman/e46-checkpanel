# E46 PT-CAN message map (500 kbps, 11-bit IDs)
Confidence: community-sourced. Anything marked (unverified) needs a live capture to confirm.

| ID | Signal | Decode | Status |
|---|---|---|---|
| 0x316 | RPM | bytes 2–3 little-endian × 0.1558 | confirmed (community) |
| 0x329 | Coolant temp | byte 1: °C = 0.75×raw − 48.373 | confirmed (community) |
| 0x545 | Warning lights | message identified; bit positions unmapped | needs live sniff |
| 0x153 | ASC1 error lamp | one bit confirmed | partial |
| 0x1F0 | ASC2 wheel speed | placeholder | unverified |
| 0x613 / 0x615 | IKE odometer/status | placeholder | unverified |
| ??? | Battery voltage | no confirmed ID | needs live capture |
| — | Oil pressure | non-M E46 likely switch-only, no sender | probably unavailable |
