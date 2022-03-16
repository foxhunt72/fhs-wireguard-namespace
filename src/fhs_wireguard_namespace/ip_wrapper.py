# network create namespace

import subprocess
import json
import ipaddress
from pprint import pprint

class Ip_Wrapper_Command_Error(LookupError):
    '''raise this when there's a lookup error for my app'''


class ip_wrapper:
    """Smal wrapper around the ip linux argument."""
    def __init__(
        self,
        ip_path=None,
        debug=False
    ):
        """Init wrapper."""
        self.ip_path = ip_path if ip_path is not None else '/bin/ip'
        self.debug = debug

    def check_namespace_name(self, namespace_name):
        """Check if namespace name is valid."""
        if namespace_name.isalnum() is False or len(namespace_name) > 15:
            raise Ip_Wrapper_Command_Error(f"namespace name not valid: {namespace_name}")
        return True

    def check_interface_name(self, interface_name):
        """Check if interface name is valid."""
        if interface_name.isalnum() is False:
            raise Ip_Wrapper_Command_Error(f"interace name not valid: {interface_name}")
        return True

    def check_address(self, address):
        """Check if address is valid."""
        try:
            ip = ipaddress.ip_address(address)

            if isinstance(ip, ipaddress.IPv4Address):
                return '4'
            elif isinstance(ip, ipaddress.IPv6Address):
                return '6'
        except ValueError:
            return None

    def check_subnet(self, subnet):
        """Check if subnet is valid."""
        # TODO subnet check, ipv4 and ipv6
        return '4'

    def run_ip(
        self,
        arguments: list,
        namespace=None,
        stdin=None
    ):
        """Run ip with arguments."""
        if namespace is not None:
            self.check_namespace_name(namespace)
            arguments.insert(0, '-n')
            arguments.insert(1, namespace)
        run_is=[self.ip_path, "-j"] + arguments
        if self.debug:
            pprint(run_is)
        result = subprocess.run(run_is, capture_output=True, input=stdin)
        if self.debug:
            pprint(result)
        if result is None:
            return None
        if result.returncode != 0:
            raise Ip_Wrapper_Command_Error(f"result command: {result.stderr}")
        if result.stdout == b'':
            return True
        result_list=json.loads(result.stdout)
        return result_list
 
    def netns_list(self):
        """Get a list of namespaces."""
        result = self.run_ip(['netns', 'list'])
        namespaces = []
        if result == True:
            return namespaces
        namespaces.extend(namespace['name'] for namespace in result)
        return namespaces

    def netns_add(self, namespace):
        """Create a namespace."""
        if namespace.isalnum() is False:
            raise ValueError('namespace needs to be alpha numeric.')
        result = self.run_ip(['netns', 'add', namespace])
        return result

    def link_add_wireguard(self, interface, namespace=None):
        """Create a link.
        ip link add dev wg0 type wireguard
        """
        self.check_interface_name(interface)
        result = self.run_ip(['link', 'add', 'dev', interface, 'type', 'wireguard'], namespace)
        return result

    def link_set_netns(self, interface, namespace, from_namespace=None):
        """Set a link to a namespace."""
        self.check_interface_name(interface)
        self.check_namespace_name(namespace)
    
        result = self.run_ip(['link', 'set', interface, 'netns', namespace], from_namespace)
        return result

    def link_interface_up(self, interface,  *, mtu=None, namespace=None):
        """Set a link to up."""
        self.check_interface_name(interface)
        execute_list = ['link', 'set', 'up', 'dev', interface]
        if mtu is not None:
            execute_list.insert(2, 'mtu')
            execute_list.insert(3, str(mtu))
        pprint(execute_list)
        result = self.run_ip(execute_list, namespace)
        return result

    def link_show_interface(self, interface, namespace=None):
        """Show interface."""
        self.check_interface_name(interface)
        result = self.run_ip(['link', 'show', interface], namespace)
        return result

    def address_add(self, interface, address, namespace=None):
        """Add address to interface."""
        self.check_interface_name(interface)
        if isinstance(address, str): address = [address]

        for addr in address:
            proto = '-6' if ':' in addr else '-4'
            result = self.run_ip([proto, 'address', 'add', addr, 'dev', interface], namespace)
            print(f">>>{result}<<<")
        return result

    def wg_setconf_in_namespace(self,interface, namespace, config):
        """Set wireguard config in namespace."""
        self.check_interface_name(interface)
        self.check_namespace_name(namespace)

        result = self.run_ip(
            ['netns', 'exec', namespace, 'wg', 'setconf', interface, '/dev/stdin'],
            stdin = config.encode('utf-8')
        )
        return result

    def route_get(self, address):
        """Get route info."""
        if address == 'default':
            result = self.run_ip(['route', 'show', 'default'])
            return result
        if self.check_address(address) is not None:
            result = self.run_ip(['route', 'get', address])
            return result
        else:
            raise ValueError(f'address <{address}> not valid.')
    
    def link_show_dev(self, interface):
        """Show interface."""
        self.check_interface_name(interface)
        result = self.run_ip(['link', 'show', 'dev', interface])
        return result

    def route_add_default(self, interface, *, namespace=None):
        """Add default route."""
        self.check_interface_name(interface)
        result = self.run_ip(['route', 'add', 'default', 'dev', interface], namespace=namespace)
        return result

    def route_add_subnet(self, interface, subnet, *, namespace=None):
        """Add subnet route."""
        self.check_interface_name(interface)
        if subnet == 'default':
            result = self.route_add_default(interface, namespace=namespace)
            return result
        self.check_subnet(subnet)
        result = self.run_ip(['route', 'add', subnet , 'dev', interface], namespace=namespace)
        return result