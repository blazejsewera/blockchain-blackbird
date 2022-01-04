from Pyro5 import api
from Pyro5.client import Proxy, _RemoteMethod, _StreamResultIterator
from Pyro5.protocol import ReceivingMessage
from Pyro5.server import Daemon as PDaemon
from Pyro5.server import expose

ProxyProperty = ReceivingMessage | _StreamResultIterator | _RemoteMethod | None


def locate_ns() -> Proxy:
    return api.locate_ns()


def invoke(method: ProxyProperty, *args, **kwargs):
    if isinstance(method, _RemoteMethod):
        return method(*args, **kwargs)
    else:
        raise TypeError(f"{method} could not be invoked, is it a field?")


def get_all_uris_as_dict(prefix: str) -> dict[str, str]:
    ns = locate_ns()
    return invoke(ns.list, prefix)


def get_all_uris(prefix: str) -> list[str]:
    objs = get_all_uris_as_dict(prefix)
    return list(objs.values())


def proxy_of(uri: str) -> Proxy:
    return Proxy(uri)


class Daemon(PDaemon):
    ns = locate_ns()

    registered_names: list[str] = []

    def register(self, obj_or_class: object, ns_name: str):
        """Register an object or class in daemon and nameserver."""
        uri = super().register(obj_or_class)
        invoke(self.ns.register, ns_name, uri)
        self.registered_names.append(ns_name)

    def shutdown(self):
        for rname in self.registered_names:
            invoke(self.ns.remove, rname)
            print(f"> removed {rname} from ns")
        super().shutdown()

    def start(self):
        print(f"> starting daemon")
        try:
            super().requestLoop()
        except Exception:
            pass
        finally:
            print("\n> shutting down...")
            self.shutdown()
            print("> done")


expose  # re-export
