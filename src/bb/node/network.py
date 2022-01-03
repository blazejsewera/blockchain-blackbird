from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    uid: str = ""


class Network:
    nodes: list[Node] = []

    def add_node(self, node: Node):
        self.nodes.append(node)

    def remove_node(self, node: Node):
        self.nodes.remove(node)
