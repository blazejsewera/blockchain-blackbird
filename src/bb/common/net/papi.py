from Pyro5 import api
from Pyro5.client import Proxy, _RemoteMethod, _StreamResultIterator
from Pyro5.protocol import ReceivingMessage

ProxyProperty = ReceivingMessage | _StreamResultIterator | _RemoteMethod | None


def invoke(method: ProxyProperty, *args, **kwargs):
    if isinstance(method, _RemoteMethod):
        return method(*args, **kwargs)
    else:
        raise TypeError(f"{method} could not be invoked, is it a field?")


def get_all_uris_as_dict(prefix: str) -> dict[str, str]:
    ns: Proxy = api.locate_ns()
    return invoke(ns.list, prefix)


def get_all_uris(prefix: str) -> list[str]:
    objs = get_all_uris_as_dict(prefix)
    return list(objs.values())


def proxy_of(uri: str) -> Proxy:
    return Proxy(uri)
