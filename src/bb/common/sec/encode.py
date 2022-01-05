import base64

from bb.common.config import DEFAULT_ENCODING


def hex_to_bytes(h: str) -> bytes:
    return bytes.fromhex(h)


def bytes_to_hex(b: bytes) -> str:
    return b.hex()


def str_to_bytes(s: str) -> bytes:
    return s.encode(DEFAULT_ENCODING)


def bytes_to_str(b: bytes) -> str:
    return b.decode(DEFAULT_ENCODING)


def bytes_to_base64_str(b: bytes) -> str:
    return bytes_to_str(base64.b64encode(b))


def base64_str_to_bytes(b64: str) -> bytes:
    return base64.b64decode(b64)
