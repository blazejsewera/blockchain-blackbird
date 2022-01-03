import unittest
from datetime import datetime as Timestamp
from block import Data, Transaction, Block


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
