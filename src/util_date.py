import re
import datetime
import dateutil.relativedelta
from dateutil.tz import tzlocal
import maya
import dateparser  # type: ignore

# Don't change the date formats! This will break parsing
DATE_FMT_GIT = "%a, %d %b %Y %H:%M:%S %z"  # E.g. "Thu, 27 Jul 2023 13:15:26 +0200". Git commit times, human readable
DATE_FMT_EXPIRE_YMD = "%Y-%m-%d"  # E.g. "2023-07-27". Machine sortable. Used in notes refspec
DATE_FMT_EXPIRE_HMz = "%H.%M%z"   # E.g. "13.14+0200". Machine sortable
DATE_FMT_EXPIRE = f"{DATE_FMT_EXPIRE_YMD}/{DATE_FMT_EXPIRE_HMz}"  # E.g. "2023-07-27/13.14+0200". Used in branch-names, machine sortable

def parse_fuzzy_time(fuzzy_time: str) -> datetime.datetime:
    """
    Parse fuzzy date expressions into datetime objects using a consistent approach.
    For relative day-based expressions, we use datetime.timedelta for consistent DST handling.
    For other expressions, we fall back to maya's parser.
    """
    now = datetime.datetime.now(tzlocal())
    
    # Handle "now" and "today" specially
    if fuzzy_time.lower() in ["now", "today"]:
        return now
    
    # Handle "tomorrow" specially
    if fuzzy_time.lower() == "tomorrow":
        return now + datetime.timedelta(days=1)
    
    # Check for patterns like "in X days/weeks" or "now in X days/weeks"
    # This handles expressions like "in 3 weeks", "in 21 days", "now in 3 weeks", etc.
    days_pattern = r'(?:now\s+)?in\s+(\d+)\s*(?:day|days|d)s?'
    weeks_pattern = r'(?:now\s+)?in\s+(\d+)\s*(?:week|weeks|w)s?'
    
    days_match = re.match(days_pattern, fuzzy_time.lower())
    weeks_match = re.match(weeks_pattern, fuzzy_time.lower())
    
    if days_match:
        days = int(days_match.group(1))
        return now + datetime.timedelta(days=days)
    
    if weeks_match:
        weeks = int(weeks_match.group(1))
        return now + datetime.timedelta(days=weeks * 7)
    
    # For everything else, fall back to maya
    dt = maya.when(fuzzy_time)
    if dt.timezone == 'UTC':
        maya_dt: datetime.datetime = dt.datetime().astimezone(tzlocal())
        return maya_dt
    maya_dt = dt.datetime()
    return maya_dt

def parse_expire_date(expiry_formatted: str, prefix_discard: str = "") -> dict:
    """ Parse a string formatted as `DATE_FMT_EXPIRE` with an optional prefix to discard """
    ret = {}

    re_date     = r"(?P<date>\d{4}-\d{2}-\d{2})"
    re_time     = r"(?P<time>\d+\.\d+)"
    re_tzoffset = r"(?:(?P<offset>[+-]\d{4}))?"
    re_artifact = rf"{prefix_discard}{re_date}/{re_time}{re_tzoffset}"

    match = re.search(re_artifact, expiry_formatted)
    ret['date']     = match.group('date') if match else None
    ret['time']     = match.group('time') if match else None
    ret['tzoffset'] = match.group('offset') if match else None
    return ret

def date_fuzzy2expiryformat(fuzzy_date: str) -> str:
    """Convert fuzzy date/time string to ``DATE_FMT_EXPIRE`` in local time."""

    dt_obj = parse_fuzzy_time(fuzzy_date)
    dt_obj = dt_obj.astimezone(tzlocal())
    return datetime.datetime.strftime(dt_obj, DATE_FMT_EXPIRE)

def date_parse_formatted(date_string: str, date_format: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_string, date_format)

def date_formatted2unix(date_string: str, date_format: str) -> float:
    """ E.g. `date_formatted2unix("Wed, 21 Jun 2023 14:13:31 +0200", "%a, %d %b %Y %H:%M:%S %z")` """
    unix_time = date_parse_formatted(date_string=date_string, date_format=date_format).timestamp()
    return unix_time

def format_timespan(dt_from: datetime.datetime, dt_to: datetime.datetime) -> str:
    delta = dateutil.relativedelta.relativedelta(dt_to, dt_from)

    if delta.days != 0:
        delta_formatted = f'{delta.days}days {delta.hours:2}h {delta.minutes:2}m'
    elif delta.hours != 0:
        delta_formatted = f'{delta.hours:2}hrs {delta.minutes:2}min'
    else:
        delta_formatted = f'{delta.minutes:2}minutes'

    return "{:>15}".format(delta_formatted)  # right-adjust
