"""Tests for OCEL import helpers."""
import datetime

import pytest

from opql.ocel.ocelimport import convert_timestamp

UTC = datetime.UTC


@pytest.mark.parametrize("raw, expected", [
    (b"2023-04-05T06:07:08+00:00", datetime.datetime(2023, 4, 5, 6, 7, 8, tzinfo=UTC)),
    (b"2023-04-05T06:07:08Z", datetime.datetime(2023, 4, 5, 6, 7, 8, tzinfo=UTC)),
    (b"2023-04-05T06:07:08+0000", datetime.datetime(2023, 4, 5, 6, 7, 8, tzinfo=UTC)),
    (b"2023-04-05T06:07:08.123+00:00",
     datetime.datetime(2023, 4, 5, 6, 7, 8, 123000, tzinfo=UTC)),
    (b"2023-04-05T06:07:08.123456+00:00",
     datetime.datetime(2023, 4, 5, 6, 7, 8, 123456, tzinfo=UTC)),
    (b"2023-04-05T06:07:08.123456Z",
     datetime.datetime(2023, 4, 5, 6, 7, 8, 123456, tzinfo=UTC)),
    (b"2023-04-05T06:07:08+05:30",
     datetime.datetime(2023, 4, 5, 6, 7, 8,
                       tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))),
    (b"2023-04-05T06:07:08-08:00",
     datetime.datetime(2023, 4, 5, 6, 7, 8,
                       tzinfo=datetime.timezone(datetime.timedelta(hours=-8)))),
])
def test_offset_forms_parse_to_the_same_instant(raw, expected):
    """The offset spellings OCEL logs actually contain. These all parsed before
    the switch to fromisoformat and must keep parsing to identical values."""
    assert convert_timestamp(raw) == expected


def test_timestamps_without_a_timezone_are_rejected():
    """A naive datetime cannot be compared against an aware one — it raises
    TypeError. olaglead compares event timestamps directly, so a naive value
    would turn an import-time rejection into a crash mid-query. fromisoformat
    accepts naive input, so the converter has to reject it explicitly."""
    with pytest.raises(ValueError):
        convert_timestamp(b"2023-04-05T06:07:08")

    with pytest.raises(ValueError):
        convert_timestamp(b"2023-04-05T06:07:08.123456")


def test_garbage_is_rejected():
    with pytest.raises(ValueError):
        convert_timestamp(b"not a timestamp")


def test_parsed_timestamps_are_mutually_comparable():
    """The property that matters downstream: any two parsed timestamps can be
    ordered without a TypeError, whatever offset they were written in."""
    stamps = [convert_timestamp(r) for r in [
        b"2023-04-05T06:07:08+00:00",
        b"2023-04-05T06:07:08Z",
        b"2023-04-05T11:37:08+05:30",
        b"2023-04-04T22:07:08-08:00",
    ]]

    assert len(set(stamps)) == 1  # same instant, four spellings
    assert sorted(stamps) == stamps
