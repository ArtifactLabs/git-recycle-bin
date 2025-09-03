import datetime
import dateparser
import pytest
from dateutil.tz import tzlocal
from git_recycle_bin.utils.date import (
    parse_fuzzy_time,
    parse_expire_date,
    date_formatted2unix,
    format_timespan,
    DATE_FMT_GIT,
    DATE_FMT_EXPIRE,
    date_fuzzy2expiryformat,
)


def test_parse_fuzzy_time_now():
    dt = parse_fuzzy_time('now')
    assert isinstance(dt, datetime.datetime)


def test_parse_expire_date():
    s = 'pre/2024-01-02/12.00+0100'
    assert parse_expire_date(s, 'pre/') == {'date': '2024-01-02', 'time': '12.00', 'tzoffset': '+0100'}


def test_parse_expire_datetime():
    p = "artifact/expire/"
    assert parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12")       == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12/")      == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12/foo")   == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12/2023-08-17/06.02/foo")   == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12+0200")  == {"date":"2023-07-27", "time":"16.12", "tzoffset":"+0200"}
    assert parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12+0200/") == {"date":"2023-07-27", "time":"16.12", "tzoffset":"+0200"}
    assert parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12-0200")  == {"date":"2023-07-27", "time":"16.12", "tzoffset":"-0200"}
    assert parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12-03")    == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert parse_expire_date(prefix_discard="", expiry_formatted="2023-07-27/16.12")  == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert parse_expire_date(prefix_discard="", expiry_formatted="2023-07-27/16.12/") == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}

def test_parse_expire_datetime_invalid():
    assert parse_expire_date(prefix_discard="artifact/expire/", expiry_formatted="artifact/expire/30d/") == {"date":None, "time":None, "tzoffset":None}

def test_date_formatted2unix():
    s = 'Wed, 21 Jun 2023 14:13:31 +0200'
    assert date_formatted2unix(s, DATE_FMT_GIT) == 1687349611

def test_absolute_date():
    expected = dateparser.parse("2023-07-27 CEST", settings={"RETURN_AS_TIMEZONE_AWARE": True})
    expected = expected.astimezone(tzlocal()).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("2023-07-27 CEST") == expected

    expected = dateparser.parse("Mon, 1 Feb 1994 21:21:42 GMT", settings={"RETURN_AS_TIMEZONE_AWARE": True})
    expected = expected.astimezone(tzlocal()).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("Mon, 1 Feb 1994 21:21:42 GMT") == expected


def test_format_timespan():
    a = datetime.datetime(2023,1,1, tzinfo=tzlocal())
    b = datetime.datetime(2023,1,2,3,4, tzinfo=tzlocal())
    assert format_timespan(a, b).strip() == '1days  3h  4m'


def test_date_fuzzy2expiryformat_absolute():
    s = '2024-01-02 12:00 UTC'
    res = date_fuzzy2expiryformat(s)
    parsed = parse_expire_date(res)
    assert parsed['date'] == '2024-01-02'
    assert parsed['time'] is not None


def test_date_fuzzy2expiryformat_relative():
    res = date_fuzzy2expiryformat('in 1 day')
    parsed = parse_expire_date(res)
    assert parsed['date'] is not None

def test_relative_date():
    assert date_fuzzy2expiryformat("now") == datetime.datetime.now(tzlocal()).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("today") == datetime.datetime.now(tzlocal()).strftime(DATE_FMT_EXPIRE)

    assert date_fuzzy2expiryformat("tomorrow") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=1)).strftime(DATE_FMT_EXPIRE)

    assert date_fuzzy2expiryformat("now in 3 weeks") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("now in 3 week") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("now in 3weeks") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("in 3 weeks") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("in 3weeks") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("in 3week") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("in 3w") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(DATE_FMT_EXPIRE)

    assert date_fuzzy2expiryformat("in 30 days") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=30)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("in 30 day") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=30)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("in 30days") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=30)).strftime(DATE_FMT_EXPIRE)
    assert date_fuzzy2expiryformat("in 30day") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=30)).strftime(DATE_FMT_EXPIRE)

    assert date_fuzzy2expiryformat("next month") == date_fuzzy2expiryformat("now in 1 month")

def test_invalid_date():
    with pytest.raises(ValueError, match="invalid datetime input"):
        date_fuzzy2expiryformat("invalid")
    with pytest.raises(ValueError, match="invalid datetime input"):
        date_fuzzy2expiryformat("Mon, 32 Feb 1994 21:21:42 GMT")
