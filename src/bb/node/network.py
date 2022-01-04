from dataclasses import dataclass, field

from bb.common.block import Block, Transaction


@dataclass
class Node:
    uid: str = ""
    blocks: list[Block] = field(default_factory=list)

    current_block: Block = field(default_factory=Block)
    current_transactions: list[Transaction] = field(default_factory=list)

    def add_transaction(self, transaction: Transaction):
        self.current_transactions.append(transaction)


class Network:
    nodes: list[Node] = []

    def add_node(self, node: Node):
        self.nodes.append(node)

    def remove_node(self, node: Node):
        self.nodes.remove(node)
