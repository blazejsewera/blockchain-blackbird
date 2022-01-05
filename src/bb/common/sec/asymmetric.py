from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)

from .encode import base64_str_to_bytes, bytes_to_base64_str, str_to_bytes
from .hash import SHA256


def __pss_padding():
    return padding.PSS(mgf=padding.MGF1(SHA256()), salt_length=padding.PSS.MAX_LENGTH)


def generate_private_key() -> rsa.RSAPrivateKey:
    DEFAULT_RSA_PUBLIC_EXPONENT = 65537
    return rsa.generate_private_key(DEFAULT_RSA_PUBLIC_EXPONENT, 1024)


def sign(message: str, private_key: rsa.RSAPrivateKey) -> str:
    message_bytes = str_to_bytes(message)
    signed_bytes = private_key.sign(message_bytes, __pss_padding(), SHA256())

    return bytes_to_base64_str(signed_bytes)


def verify(message: str, signature_base64: str, public_key: rsa.RSAPublicKey) -> bool:
    verified = True
    signature_bytes = base64_str_to_bytes(signature_base64)
    message_bytes = str_to_bytes(message)
    try:
        public_key.verify(signature_bytes, message_bytes, __pss_padding(), SHA256())
    except InvalidSignature:
        verified = False

    return verified


def encode_public_key(public_key: rsa.RSAPublicKey) -> str:
    pk_bytes = public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    return bytes_to_base64_str(pk_bytes)


def decode_public_key(public_key_base64: str) -> rsa.RSAPublicKey:
    pk_bytes = base64_str_to_bytes(public_key_base64)
    key: rsa.RSAPublicKey = load_pem_public_key(pk_bytes)  # type: ignore
    return key


# re-export
RSAPrivateKey = rsa.RSAPrivateKey
RSAPublicKey = rsa.RSAPublicKey
