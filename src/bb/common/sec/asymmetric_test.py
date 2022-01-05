import unittest

from .asymmetric import decode_public_key, encode_public_key, generate_private_key


class TestAsymmetric(unittest.TestCase):
    def test_encode_public_key(self):
        # given
        private_key = generate_private_key()
        public_key = private_key.public_key()
        PEM_RSA_PUBLIC_KEY_HEADER = "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlHZk1BMEdDU3FHU0liM0RRRUJBUVVBQTRHTkFEQ0JpUUtCZ1F"

        # when
        tested = encode_public_key(public_key)

        # then
        self.assertRegex(tested, f"^{PEM_RSA_PUBLIC_KEY_HEADER}")

    def test_decode_public_key(self):
        # given
        private_key = generate_private_key()
        public_key = private_key.public_key()
        encoded_pk = encode_public_key(public_key)

        # when
        tested = decode_public_key(encoded_pk)

        # then
        self.assertEqual(encode_public_key(tested), encoded_pk)


if __name__ == "__main__":
    unittest.main()
