from cryptography.hazmat.primitives.hashes import SHA256, Hash


def sha256(str_to_hash: str, to_bytes=False):
    b = str_to_hash.encode("utf-8")

    digest = Hash(SHA256())
    digest.update(b)
    hash_bytes = digest.finalize()

    if to_bytes:
        return hash_bytes
    return hash_bytes.hex()
