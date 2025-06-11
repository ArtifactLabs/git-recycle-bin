import pytest
import datetime
from dateutil.tz import tzlocal
import dateparser

from src import git_recycle_bin as grb  # DUT

def test_trim_all_lines():
    assert grb.trim_all_lines("  hello\n  world\n") == "hello\nworld\n"

def test_prefix_lines():
    assert grb.prefix_lines("hello\nworld\n", "prefix: ") == "prefix: hello\nprefix: world"

def test_extract_gerrit_change_id():
    commit_message = "Some changes\n\nChange-Id: I8473b920f2b0d34f2ef5ddbfdf3bea5db12c99d7"
    assert grb.extract_gerrit_change_id(commit_message) == "I8473b920f2b0d34f2ef5ddbfdf3bea5db12c99d7"

def test_string_trunc_ellipsis():
    assert grb.string_trunc_ellipsis(5, "hello world") == "he..."

def test_date_formatted2unix():
    assert grb.date_formatted2unix("Wed, 21 Jun 2023 14:13:31 +0200", "%a, %d %b %Y %H:%M:%S %z") == 1687349611

def test_absolute_date():
    expected = dateparser.parse("2023-07-27 CEST", settings={"RETURN_AS_TIMEZONE_AWARE": True})
    expected = expected.astimezone(tzlocal()).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("2023-07-27 CEST") == expected

    expected = dateparser.parse("Mon, 1 Feb 1994 21:21:42 GMT", settings={"RETURN_AS_TIMEZONE_AWARE": True})
    expected = expected.astimezone(tzlocal()).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("Mon, 1 Feb 1994 21:21:42 GMT") == expected

def test_relative_date():
    assert grb.date_fuzzy2expiryformat("now") == datetime.datetime.now(tzlocal()).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("today") == datetime.datetime.now(tzlocal()).strftime(grb.DATE_FMT_EXPIRE)

    assert grb.date_fuzzy2expiryformat("tomorrow") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=1)).strftime(grb.DATE_FMT_EXPIRE)

    assert grb.date_fuzzy2expiryformat("now in 3 weeks") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("now in 3 week") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("now in 3weeks") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("in 3 weeks") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("in 3weeks") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("in 3week") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("in 3w") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=21)).strftime(grb.DATE_FMT_EXPIRE)

    assert grb.date_fuzzy2expiryformat("in 30 days") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=30)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("in 30 day") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=30)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("in 30days") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=30)).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("in 30day") == (datetime.datetime.now(tzlocal()) + datetime.timedelta(days=30)).strftime(grb.DATE_FMT_EXPIRE)

    assert grb.date_fuzzy2expiryformat("next month") == grb.date_fuzzy2expiryformat("now in 1 month")

def test_invalid_date():
    with pytest.raises(ValueError, match="invalid datetime input"):
        grb.date_fuzzy2expiryformat("invalid")
    with pytest.raises(ValueError, match="invalid datetime input"):
        grb.date_fuzzy2expiryformat("Mon, 32 Feb 1994 21:21:42 GMT")

def test_parse_expire_datetime():
    p = "artifact/expire/"
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12")       == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12/")      == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12/foo")   == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12/2023-08-17/06.02/foo")   == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12+0200")  == {"date":"2023-07-27", "time":"16.12", "tzoffset":"+0200"}
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12+0200/") == {"date":"2023-07-27", "time":"16.12", "tzoffset":"+0200"}
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12-0200")  == {"date":"2023-07-27", "time":"16.12", "tzoffset":"-0200"}
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted="artifact/expire/2023-07-27/16.12-03")    == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert grb.parse_expire_date(prefix_discard="", expiry_formatted="2023-07-27/16.12")  == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    assert grb.parse_expire_date(prefix_discard="", expiry_formatted="2023-07-27/16.12/") == {"date":"2023-07-27", "time":"16.12", "tzoffset":None}

def test_parse_expire_datetime_invalid():
    assert grb.parse_expire_date(prefix_discard="artifact/expire/", expiry_formatted="artifact/expire/30d/") == {"date":None, "time":None, "tzoffset":None}

def test_url_redact():
    assert grb.url_redact(url="https://foo:pass@service/my/repo.git", replacement="REDACTED") == "https://foo:REDACTED@service/my/repo.git"
    assert grb.url_redact(url="https://foo@service/my/repo.git", replacement="REDACTED")      == "https://foo@service/my/repo.git"
    assert grb.url_redact(url="https://service/my/repo.git", replacement="REDACTED")          == "https://service/my/repo.git"
    assert grb.url_redact(url="https://service/my/re:po.git", replacement="REDACTED")         == "https://service/my/re:po.git"
    assert grb.url_redact(url="https://service/my/re:po@hmm.git", replacement="REDACTED")     == "https://service/my/re:po@hmm.git"

    assert grb.url_redact(url="ssh://foo:pass@service/my/repo.git", replacement="REDACTED")   == "ssh://foo:REDACTED@service/my/repo.git"
    assert grb.url_redact(url="ssh://foo@service/my/repo.git", replacement="REDACTED")        == "ssh://foo@service/my/repo.git"
    assert grb.url_redact(url="ssh://service/my/repo.git", replacement="REDACTED")            == "ssh://service/my/repo.git"
    assert grb.url_redact(url="ssh://service/my/re:po.git", replacement="REDACTED")           == "ssh://service/my/re:po.git"
    assert grb.url_redact(url="ssh://service/my/re:po@hmm.git", replacement="REDACTED")       == "ssh://service/my/re:po@hmm.git"

    assert grb.url_redact(url="foo:pass@service/my/repo.git", replacement="REDACTED") == "foo:pass@service/my/repo.git"
    assert grb.url_redact(url="foo@service/my/repo.git", replacement="REDACTED")      == "foo@service/my/repo.git"
    assert grb.url_redact(url="service/my/repo.git", replacement="REDACTED")          == "service/my/repo.git"
    assert grb.url_redact(url="service/my/re:po.git", replacement="REDACTED")         == "service/my/re:po.git"
    assert grb.url_redact(url="service/my/re:po@hmm.git", replacement="REDACTED")     == "service/my/re:po@hmm.git"
