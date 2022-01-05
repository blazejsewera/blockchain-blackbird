from cryptography.hazmat.primitives.hashes import SHA256, Hash

from bb.common.config import DEFAULT_ENCODING
from bb.common.sec.encode import bytes_to_hex


def sha256(str_to_hash: str):
    b = str_to_hash.encode(DEFAULT_ENCODING)

    digest = Hash(SHA256())
    digest.update(b)
    hash_bytes = digest.finalize()

    return bytes_to_hex(hash_bytes)


# re-export
SHA256
Hash
