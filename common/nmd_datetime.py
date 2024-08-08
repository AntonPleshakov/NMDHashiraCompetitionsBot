from datetime import timezone, datetime, timedelta
from typing import List

_moscow_timezone = timezone(timedelta(hours=3))


def nmd_now() -> datetime:
    return datetime.now(_moscow_timezone)


def _contains(elements: List[str], dt_format: str) -> bool:
    return any([v in dt_format for v in elements])


def _sync_with_default(dt: datetime, default: datetime, dt_format: str) -> datetime:
    if "%y" not in dt_format.lower():
        dt = dt.replace(year=default.year)
    if not _contains(["%b", "%B", "%m", "%-m"], dt_format):
        dt = dt.replace(month=default.month)
    if not _contains(["%a", "%w", "%d", "%-d"], dt_format.lower()):
        dt = dt.replace(day=default.day)
    if dt < default:
        dt = dt.replace(year=dt.year + 1)
    return dt


def nmd_parse_datetime(
    dt: str, dt_format: str, sync_with_now: bool = False
) -> datetime:
    now = nmd_now()
    res = datetime.strptime(dt, dt_format).replace(tzinfo=_moscow_timezone)
    if sync_with_now:
        res = _sync_with_default(res, now, dt_format)
    return res
