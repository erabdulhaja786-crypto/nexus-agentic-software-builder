import time
import uuid


def uuid7():
    """
    Pure-Python UUIDv7-compatible generator.

    This avoids the native uuid_utils DLL that is
    blocked by Windows Application Control.
    """

    timestamp_ms = int(time.time() * 1000)

    random_uuid = uuid.uuid4()

    timestamp = timestamp_ms & ((1 << 48) - 1)

    value = (
        (timestamp << 80)
        | (0x7 << 76)
        | ((random_uuid.int >> 62) & ((1 << 12) - 1)) << 64
        | (0x2 << 62)
        | (random_uuid.int & ((1 << 62) - 1))
    )

    return uuid.UUID(int=value)