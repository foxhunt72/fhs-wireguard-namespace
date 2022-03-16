"""Wiregurd configure."""

from .network_create_namespace import netns_create
from .network_create_wireguard import wireguard_create, move_interface_to_namespace, wireguard_check_exists
from .network_configure_wireguard import wireguard_configure


def create_wg_if_in_ns(interface_name, namespace_name, wc = None):
    """Create a wireguard interface."""
    result = netns_create(namespace_name)
    if result is None:
        print("Namespace created successfully")
    else:
        if 'Namespace already exists' not in result:
            print(result)
            return 1
    if wireguard_check_exists(interface_name, namespace_name) is False:
        result = wireguard_create(interface_name)
        if result is None:
            print("Wireguard interface created successfully")
        else:
            print(result)
            return 1
        result = move_interface_to_namespace(interface_name, namespace_name)
        if result is None:
            print("Interface moved to namespace successfully")
        else:
            print(result)
            return 1
    result = wireguard_configure(interface_name, namespace_name, wc=wc)
    if result is None:
        print("Wireguard interface configured successfully")
    else:
        print(result)
        return 1
    return 0

