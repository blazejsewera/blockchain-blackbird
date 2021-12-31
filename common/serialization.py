import json
from dataclasses import asdict
from typing import Union
from common.block import Block


def to_json(block: Block) -> str:
    return json.dumps(asdict(block))


def from_json(serialized_block: Union[str, dict]) -> Block:
    if type(serialized_block) == str:
        return Block.of(json.loads(serialized_block))
    return Block.of(serialized_block)
