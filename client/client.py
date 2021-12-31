from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

DEFAULT_RSA_PUBLIC_EXPONENT = 65537

pk = rsa.generate_private_key(DEFAULT_RSA_PUBLIC_EXPONENT, 1024)

print(pk.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH))
