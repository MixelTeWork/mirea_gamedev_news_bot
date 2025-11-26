def parse_int[T](v: str, default: T = None) -> int | T:
    try:
        return int(v)
    except Exception:
        return default
