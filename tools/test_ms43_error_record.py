"""Tests for ms43_error_record.py against the 16 real records captured
via INPA on the 325iT and 325xi (see sample_data/ms43_error_records.json
and docs/reference/inpa/*MS430DS0_fault-memory.pdf).

Run with:  pytest tools/test_ms43_error_record.py -v

What's checked against INPA's own decoded output (real ground truth):
    - fault_number, error_frequency, logistic_counter
    - elapsed_hours(), reconstructed from the record's operating-hours
      snapshot plus the DME's counter at capture time, checked against
      INPA's printed "aufgetreten vor (rel. BZ)" value

What's checked structurally instead (bit-unpacking mechanics, per the
§8.2 layout, not independently re-derivable from INPA's fault-specific
condition-flag text labels):
    - record length validation
    - status byte fields are the right types and condition_flags has 4 entries
    - environmental_bytes passes the 4 raw bytes through unchanged
"""

import json
from pathlib import Path

import pytest

from ms43_error_record import RECORD_LENGTH, elapsed_hours, parse_record

FIXTURE_PATH = Path(__file__).parent.parent / "sample_data" / "ms43_error_records.json"


def load_fixture_records():
    with open(FIXTURE_PATH) as f:
        return json.load(f)["records"]


FIXTURE_RECORDS = load_fixture_records()


def _id(record):
    return f"{record['car']}-fault{record['fault_number']}"


@pytest.mark.parametrize("fixture", FIXTURE_RECORDS, ids=_id)
def test_fault_number(fixture):
    parsed = parse_record(fixture["errorcode_hex"])
    assert parsed.fault_number == fixture["fault_number"]


@pytest.mark.parametrize("fixture", FIXTURE_RECORDS, ids=_id)
def test_error_frequency(fixture):
    parsed = parse_record(fixture["errorcode_hex"])
    assert parsed.error_frequency == fixture["error_frequency"]


@pytest.mark.parametrize("fixture", FIXTURE_RECORDS, ids=_id)
def test_logistic_counter(fixture):
    parsed = parse_record(fixture["errorcode_hex"])
    assert parsed.logistic_counter == fixture["logistic_counter"]


@pytest.mark.parametrize("fixture", FIXTURE_RECORDS, ids=_id)
def test_elapsed_hours_matches_inpa(fixture):
    parsed = parse_record(fixture["errorcode_hex"])
    hours = elapsed_hours(parsed, fixture["dme_current_counter_raw"])
    assert hours == pytest.approx(fixture["expected_elapsed_hours"], abs=0.05)


@pytest.mark.parametrize("fixture", FIXTURE_RECORDS, ids=_id)
def test_status_and_environmental_bytes_are_well_formed(fixture):
    parsed = parse_record(fixture["errorcode_hex"])
    assert isinstance(parsed.status.relevant, bool)
    assert isinstance(parsed.status.present, bool)
    assert isinstance(parsed.status.debounce, bool)
    assert isinstance(parsed.status.sporadic, bool)
    assert len(parsed.status.condition_flags) == 4
    assert all(isinstance(flag, bool) for flag in parsed.status.condition_flags)

    raw = bytes.fromhex(fixture["errorcode_hex"].replace(" ", ""))
    assert parsed.environmental_bytes == raw[4:8]


def test_rejects_wrong_length_record():
    with pytest.raises(ValueError):
        parse_record("25 61 01 28 01 32 5B 00 B7")  # 9 bytes, one short


def test_record_length_constant_matches_spec():
    assert RECORD_LENGTH == 10
