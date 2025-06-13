import datetime
from dateutil.tz import tzlocal
from util_date import (
    parse_fuzzy_time,
    parse_expire_date,
    date_formatted2unix,
    format_timespan,
    DATE_FMT_GIT,
    date_fuzzy2expiryformat,
)


def test_parse_fuzzy_time_now():
    dt = parse_fuzzy_time('now')
    assert isinstance(dt, datetime.datetime)


def test_parse_expire_date():
    s = 'pre/2024-01-02/12.00+0100'
    assert parse_expire_date(s, 'pre/') == {'date': '2024-01-02', 'time': '12.00', 'tzoffset': '+0100'}


def test_date_formatted2unix():
    s = 'Wed, 21 Jun 2023 14:13:31 +0200'
    assert date_formatted2unix(s, DATE_FMT_GIT) == 1687349611


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

