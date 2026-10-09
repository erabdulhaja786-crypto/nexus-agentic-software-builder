import json


# ============================================================
# ORJSON COMPATIBILITY OPTIONS
# ============================================================

OPT_APPEND_NEWLINE = 1
OPT_INDENT_2 = 2
OPT_NAIVE_UTC = 4
OPT_NON_STR_KEYS = 8
OPT_OMIT_MICROSECONDS = 16
OPT_PASSTHROUGH_DATACLASS = 2048
OPT_PASSTHROUGH_DATETIME = 512
OPT_PASSTHROUGH_SUBCLASS = 256
OPT_SERIALIZE_DATACLASS = 0
OPT_SERIALIZE_NUMPY = 16
OPT_SERIALIZE_UUID = 0
OPT_SORT_KEYS = 32
OPT_STRICT_INTEGER = 64
OPT_UTC_Z = 128


# ============================================================
# EXCEPTION COMPATIBILITY
# ============================================================

JSONDecodeError = json.JSONDecodeError


# ============================================================
# DUMPS
# ============================================================

def dumps(
    obj,
    *,
    default=None,
    option=0
):
    """
    Pure-Python replacement for orjson.dumps().

    Returns bytes, matching orjson behavior.
    """

    indent = 2 if option & OPT_INDENT_2 else None

    sort_keys = bool(
        option & OPT_SORT_KEYS
    )

    if default is not None:

        def convert(value):
            try:
                return default(value)
            except Exception:
                raise

        result = json.dumps(
            obj,
            default=convert,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=False
        )

    else:

        result = json.dumps(
            obj,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=False,
            default=str
        )

    if option & OPT_APPEND_NEWLINE:
        result += "\n"

    return result.encode("utf-8")


# ============================================================
# LOADS
# ============================================================

def loads(obj):
    """
    Pure-Python replacement for orjson.loads().
    """

    if isinstance(obj, bytes):
        obj = obj.decode("utf-8")

    return json.loads(obj)