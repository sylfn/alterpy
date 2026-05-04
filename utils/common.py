import datetime

def to_int(val: any, default: int = 0) -> int:
    try:
        return int(val)
    except ValueError:
        return default

def stamp() -> int:
    r = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    return r.total_seconds() * 1000000 + r.microseconds

