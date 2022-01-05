from cryptography.hazmat.primitives.hashes import Hash

from bb.common.config import DEFAULT_ENCODING, DEFAULT_HASH
from bb.common.sec.encode import bytes_to_hex


def hash_hex(str_to_hash: str):
    b = str_to_hash.encode(DEFAULT_ENCODING)

    digest = Hash(DEFAULT_HASH())
    digest.update(b)
    hash_bytes = digest.finalize()

    return bytes_to_hex(hash_bytes)


# re-export
DEFAULT_HASH
Hash
