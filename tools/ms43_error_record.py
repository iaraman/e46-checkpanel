"""Parser for MS43 DS2 error-memory records.

Record layout is confirmed (rated A) in docs/REQ-001-requirements.md §8.2,
reverse-engineered from INPA's own decoded output against its raw
`Errorcode:` bytes across 16 records on two cars.

10-byte record:
    byte 0    fault number (plain decimal, not BCD)
    byte 1    status bitfield (see parse_status_byte)
    byte 2    error frequency
    byte 3    logistic counter
    bytes 4-7 four environmental values, fault-specific meaning
    bytes 8-9 operating-hours snapshot, big-endian uint16, 0.1 h/LSB

What this module does NOT do (see REQ-001 §8.2 and §10 Q21-Q22 — open
questions, not derivable from record bytes alone):
    - map fault_number to human-readable text (lives in the SGBD)
    - map environmental_bytes to named variables like TCO/N_32/VB
      (the mapping is fault-specific; e.g. fault 37 uses
      {VB, V_IGK, TCO, N_32} but fault 227 uses different variables
      in the same byte positions)
    - apply the §8.2 scaling formulas (e.g. TCO: degC = 0.75*raw - 48)
      to environmental_bytes, since without the mapping above we don't
      know which formula applies to which byte

environmental_bytes is kept as a raw 4-byte value so that once the
fault-number -> variable-mapping is captured, a scaling step can be
added on top of this parser without changing the record layout code.
"""

from dataclasses import dataclass
from typing import List

RECORD_LENGTH = 10
HOURS_PER_LSB = 0.1


@dataclass(frozen=True)
class ErrorStatus:
    """The 8 bits of byte 1, broken out per §8.2."""

    relevant: bool
    present: bool
    debounce: bool
    sporadic: bool  # True = sporadic, False = static
    condition_flags: List[bool]  # condition_flags[0] = bit 0 ... [3] = bit 3
    # condition_flags meaning is fault-specific (e.g. "Misfire CARB_A") and
    # is not decoded here — see module docstring.


@dataclass(frozen=True)
class ErrorRecord:
    fault_number: int
    status: ErrorStatus
    error_frequency: int
    logistic_counter: int
    environmental_bytes: bytes  # raw bytes 4-7, unscaled
    operating_hours_raw: int  # bytes 8-9, big-endian, 0.1 h/LSB


def parse_status_byte(byte1: int) -> ErrorStatus:
    return ErrorStatus(
        relevant=bool(byte1 & 0x80),
        present=bool(byte1 & 0x40),
        debounce=bool(byte1 & 0x20),
        sporadic=bool(byte1 & 0x10),
        condition_flags=[bool(byte1 & (1 << i)) for i in range(4)],
    )


def parse_record(hex_string: str) -> ErrorRecord:
    """Parse a 10-byte MS43 error record from a hex string.

    hex_string may contain spaces, e.g. the exact text INPA prints after
    'Errorcode:' — "25 61 01 28 01 32 5B 00 B7 F6".
    """
    data = bytes.fromhex(hex_string.replace(" ", ""))
    if len(data) != RECORD_LENGTH:
        raise ValueError(
            f"expected a {RECORD_LENGTH}-byte record, got {len(data)} bytes"
        )
    return ErrorRecord(
        fault_number=data[0],
        status=parse_status_byte(data[1]),
        error_frequency=data[2],
        logistic_counter=data[3],
        environmental_bytes=data[4:8],
        operating_hours_raw=(data[8] << 8) | data[9],
    )


def elapsed_hours(record: ErrorRecord, current_counter_raw: int) -> float:
    """Hours since the fault occurred — INPA's 'aufgetreten vor (rel. BZ)'.

    current_counter_raw is the DME's *current* operating-hours counter
    (0.1 h/LSB), which must be read separately — it is not part of the
    error record itself (REQ-001 §8.2, §10 Q22).
    """
    return (current_counter_raw - record.operating_hours_raw) * HOURS_PER_LSB
