import unittest
from dataclasses import replace
from datetime import datetime as Timestamp

from bb.common.sec.asymmetric import generate_private_key

from .block import Block, Data, Transaction


class TestData(unittest.TestCase):
    # given
    data = Data(T="data", payload="test_payload")
    serialized_data = '{"T": "data", "payload": "test_payload"}'

    def test_to_json(self):
        # when
        tested = self.data.to_json()

        # then
        self.assertEqual(tested, self.serialized_data)

    def test_from_json(self):
        # when
        tested = Data.from_json(self.serialized_data)

        # then
        self.assertEqual(tested, self.data)


class TestTransaction(unittest.TestCase):
    # given
    data = Data(T="data", payload="test_payload")
    transaction = Transaction(
        user_guid="test_user_guid", fingerprint="test_fingerprint", data=data
    )
    serialized_transaction = """\
{
    "user_guid": "test_user_guid",
    "fingerprint": "test_fingerprint",
    "data": {
        "T": "data",
        "payload": "test_payload"
    }
}"""

    def test_to_json(self):
        # when
        tested = self.transaction.to_json(indent=4)

        # then
        self.assertEqual(tested, self.serialized_transaction)

    def test_from_json(self):
        # when
        tested = Transaction.from_json(self.serialized_transaction)

        # then
        self.assertEqual(tested, self.transaction)

    def test_sign_and_verify_success(self):
        # given
        private_key = generate_private_key()
        public_key = private_key.public_key()
        tested_transaction = replace(self.transaction, fingerprint="")

        # when
        tested_transaction.sign(private_key)

        # then
        self.assertNotEqual(tested_transaction.fingerprint, "")

        # when
        verified = tested_transaction.verify(public_key)

        # then
        self.assertEqual(verified, True)

    def test_sign_and_verify_failure(self):
        # given
        first_private_key = generate_private_key()
        second_private_key = generate_private_key()
        second_public_key = second_private_key.public_key()
        tested_transaction = replace(self.transaction, fingerprint="")

        # when
        tested_transaction.sign(first_private_key)
        verified = tested_transaction.verify(second_public_key)

        # then
        self.assertEqual(verified, False)


class TestBlock(unittest.TestCase):
    # given
    data = Data(T="data", payload="test_payload")
    transaction = Transaction(
        user_guid="test_user_guid", fingerprint="test_fingerprint", data=data
    )
    block = Block(
        index=1,
        timestamp="2021-01-01T00:00:00.000",
        transactions=[transaction],
        prev_hash="test_prev_hash",
        proof=1,
    )

    serialized_block = """\
{
    "index": 1,
    "timestamp": "2021-01-01T00:00:00.000",
    "transactions": [
        {
            "user_guid": "test_user_guid",
            "fingerprint": "test_fingerprint",
            "data": {
                "T": "data",
                "payload": "test_payload"
            }
        }
    ],
    "prev_hash": "test_prev_hash",
    "proof": 1
}"""

    def test_to_json(self):
        # when
        tested = self.block.to_json(indent=4)

        # then
        self.assertEqual(tested, self.serialized_block)

    def test_from_json(self):
        # when
        tested = Block.from_json(self.serialized_block)

        # then
        self.assertEqual(tested, self.block)

    def test_get_timestamp(self):
        # given
        timestamp = Timestamp(2021, 1, 1, 0, 0, 0, 0)

        # when
        tested = self.block.get_timestamp()

        # then
        self.assertEqual(tested, timestamp)

    def test_hash(self):
        # given
        hash = "fd0613513d8e75f1f4f136f6ac65f8869690201ab76d90e1dffe492136bab3d1"

        # when
        tested = self.block.hash()

        # then
        self.assertEqual(tested, hash)


if __name__ == "__main__":
    unittest.main()
