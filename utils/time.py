from datetime import datetime
from dateutil import parser, tz


def get_datetime(time_str, default_tzinfo = None):
    """
    Parses time string into datetime object. Depending on the
    string, the resulting datetime could be either tz-aware or naive.
    This might be inconvenient for later use, e.g. in comparisons.

    User can supply an optional default_tzinfo param, that will be used
    in case tz info can not be deduced from the string

    Param time_string - string to be parsed
    Param default_tzinfo - tzinfo object to use if tz could not be
    deduced from the sting
    Returns datetime object. If the default_tzinfo is set, the datetime object is
    guaranteed to be tz-aware.
    """

    if isinstance(time_str, datetime):
        return time_str
    dt = parser.parse(
        time_str,
        default=datetime.utcfromtimestamp(0)
    )
    if dt.tzinfo is None and default_tzinfo is not None:
        dt = dt.replace(tzinfo=default_tzinfo)
    return dt


def unserialize_time(value):
    if isinstance(value, str):
        value = get_datetime(value, default_tzinfo=tz.tzutc())
    return value