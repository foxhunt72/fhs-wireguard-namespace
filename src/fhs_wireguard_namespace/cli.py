"""Console script for fh_wireguard_namespace."""
import sys

import typer

from .network_create_namespace import netns_create
from .network_create_namespace import netns_setdns
from .network_create_wireguard import wireguard_create, move_interface_to_namespace
from .network_configure_wireguard import wireguard_configure
from .create_wg_interface_in_namespace import create_wg_if_in_ns

app = typer.Typer()


@app.command()
def ns_create(namespace: str = typer.Argument(..., help="Namespace name")):
    """Create a namespace."""
    result = netns_create(namespace)
    if result is None:
        print("Namespace created successfully")
    else:
        print(result)
        return 1
    return 0

@app.command()
def ns_dns(namespace: str,
           dns: list[str],
           search: str = None,
           ):
    result = netns_setdns(namespace=namespace, dns=dns, search=search)
    if result is None:
        print("Namespace resolv.conf created successfully")
    else:
        print(result)
        return 1
    return 0


@app.command()
def wg_create(
    interface_name: str = typer.Argument(..., help="Wireguard interface name")
):
    """Create a wireguard interface."""
    result = wireguard_create(interface_name)
    if result is None:
        print("Wireguard interface created successfully")
    else:
        print(result)
        return 1
    return 0

@app.command()
def wg_config(
    interface_name: str = typer.Argument(..., help="Wireguard interface name"),
    namespace_name: str = typer.Argument(..., help="Namespace name"),
):
    """Configure a wireguard interface."""
    result = wireguard_configure(interface_name, namespace_name)
    if result is None:
        print("Wireguard interface configured successfully")
    else:
        print(result)
        return 1
    return 0


@app.command()
def move_if_to_ns(
    interface_name: str = typer.Argument(..., help="Wireguard interface name"),
    namespace_name: str = typer.Argument(..., help="Namespace name"),
):
    """Move interface to namespace."""
    result = move_interface_to_namespace(interface_name, namespace_name)
    if result is None:
        print("Interface moved to namespace successfully")
    else:
        print(result)
        return 1
    return 0

@app.command()
def wgquick_up_in_ns(
    interface_name: str = typer.Argument(..., help="Wireguard interface name"),
    namespace_name: str = typer.Argument(..., help="Namespace name"),
):
    """Move interface to namespace."""
    result = create_wg_if_in_ns(interface_name, namespace_name)
    if result is None:
        print("Interface created in namespace successfully")
    else:
        print(result)
        return 1
    return 0


if __name__ == "__main__":
    app()
