from bb.common.net.papi import Daemon
from bb.common.sec.guid import generate_guid

from .endpoint import Endpoint
from .names import NETWORK_NODE, NODE_ENDPOINT
from .network import Network, Node


def start():
    daemon = Daemon()
    network = Network()
    node = Node(network)
    endpoint = Endpoint(network, node)

    endpoint_name = f"{NODE_ENDPOINT}.{generate_guid()}"
    daemon.register(endpoint, endpoint_name)

    network_node_name = f"{NETWORK_NODE}.{generate_guid()}"
    daemon.register(node, network_node_name)

    network.scan()

    daemon.start()
    daemon.shutdown_with_ns_cleanup()
