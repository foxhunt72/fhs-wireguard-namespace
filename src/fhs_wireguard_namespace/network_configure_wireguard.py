# network create wireguard interface

from .ip_wrapper import ip_wrapper, Ip_Wrapper_Command_Error
from .network_create_namespace import netns_setdns

import wgconfig
from pprint import pprint

def wireguard_config_load(interface_name):
    """Load config from file."""
    wc = wgconfig.WGConfig(interface_name)
    try:
        wc.read_file()
    except FileNotFoundError:
        print(f"Wireguard config file not found for interface {interface_name}")
        return None
    return wc

"""
[Interface]
PrivateKey = YIEsWKsiWrJhNdze0ypYEiCK7ZwGrcrADMSggejlsWY=

[Peer]
PublicKey = mx+CoeSCAh6cqPWK84KhdSXymYdOuflGjkdXPNunfEs=
Endpoint = 212.102.34.138:1337
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
def wireguard_config_stripped(wc):
    """Strip config for wg loadcon."""
    c = []
    c.append('[Interface]')
    c.append('PrivateKey = ' + wc.interface['PrivateKey'])
    if 'ListenPort' in wc.interface:
        c.append('ListenPort = ' + str(wc.interface['ListenPort']))
    c.append('')
    for peer in wc.peers:
        p = wc.peers[peer]
        c.append('[Peer]')
        c.append(f"PublicKey = {p['PublicKey']}")
        c.append(f"Endpoint = {p['Endpoint']}")
        if 'AllowedIPs' in p:
            c.append(f'AllowedIPs = {p["AllowedIPs"]}')
        if 'PersistentKeepalive' in p:
            c.append(f'PersistentKeepalive = {p["PersistentKeepalive"]}')
        c.append('')
    return c

def wireguard_config_wg_setconf_in_namespace(
    interface_name,
    namespace_name,
    *,
    wc,
    ipw,
    debug=False
):
    cc = wireguard_config_stripped(wc)
    result = ipw.wg_setconf_in_namespace(interface_name, namespace_name, "\n".join(cc))
    if debug is True:
        pprint(result)

def wireguard_get_mtu_for_destination_address(address, *, ipw):
    try:
        result = ipw.route_get(address)
    except (Ip_Wrapper_Command_Error, ValueError) as e:
        print(e)
        return None
    try:
        endpoint_dev = result[0]['dev']
    except (ValueError, KeyError):
        return None
    try:
        result = ipw.link_show_dev(endpoint_dev)
    except Ip_Wrapper_Command_Error as e:
        print(e)
        return None
    try:
        MTU = int(result[0]['mtu'])
        return MTU
    except (ValueError, KeyError):
        return None
    return None

def wireguard_config_get_mtu(*, wc, ipw):
    """Get MTU from wc config."""
    MTU = None

    # first check is MTU is configured in interaces
    if 'MTU' in wc.interface:
        return int(wc.interfaces['MTU'])

    for peer in wc.peers:
        p = wc.peers[peer]
        endpoint = p['Endpoint']
        endpoint_address = ':'.join(endpoint.split(':')[:-1])
        MTU = wireguard_get_mtu_for_destination_address(endpoint_address, ipw=ipw)
        if MTU is not None:
            return MTU

    MTU = wireguard_get_mtu_for_destination_address('default', ipw=ipw)
    if MTU is not None:
        return MTU
    return 1500

def wireguard_config_set_route(interface_name, *, wc, ipw, namespace):
    """Set routes from wireguard config."""

    for peer in wc.peers:
        p = wc.peers[peer]
        if 'AllowedIPs' in p:
            AllowedIPs = p['AllowedIPs']
            if type(AllowedIPs) is str:
                AllowedIPs = [AllowedIPs]
            for ip in AllowedIPs:
                try:
                    ipw.route_add_subnet(interface_name, ip, namespace=namespace)
                except Ip_Wrapper_Command_Error as e:
                    if 'File exists' in str(e):
                        print(f"Route {ip} already configured")
                    else:
                        raise e from e
    return None


def wireguard_config_set_mtu_and_up(interface_name, *, wc, ipw, namespace, debug=False):
    # set_mtu_up and up
    MTU = wireguard_config_get_mtu(wc=wc, ipw=ipw)
    WG_MTU = MTU - 80
    if debug is True:
        print(f"MTU = {MTU}")
        print(f"set mtu: {WG_MTU}")
    ipw.link_interface_up(interface_name, namespace=namespace, mtu=WG_MTU)

def wireguard_config_set_address(interface_name, *, wc, ipw, namespace):
    # for i in "${ADDRESSES[@]}"; do  add_addr "$i"
    try:
        ipw.address_add(interface_name, wc.interface['Address'], namespace)
    except Ip_Wrapper_Command_Error as e:
        if 'File exists' in str(e):
            print(f"Address {wc.interface['Address']} already configured")
        else:
            raise e from e


def wireguard_configure(
    interface_name,
    namespace_name,
    *,
    wc=None,
    debug=False
):
    """Configure interface to namespace."""
    print(f"configure interface {interface_name} to namespace {namespace_name}")
    if wc is None:
        wc = wireguard_config_load(interface_name)
        if wc is None:
            return "error: can't load config"
    ipw = ip_wrapper()
    if debug is True:
        print('INTERFACE DATA:')
        pprint(wc.interface)
        print('PEER DATA:')
        pprint(wc.peers)
        print(len(wc.peers))


    wireguard_config_wg_setconf_in_namespace(interface_name, namespace_name, wc=wc, ipw=ipw)
    wireguard_config_set_address(interface_name, wc=wc, ipw=ipw, namespace=namespace_name)
    wireguard_config_set_mtu_and_up(interface_name, wc=wc, ipw=ipw, namespace=namespace_name, debug=debug)
    # set_dns
    if debug is True:
        print('check dns')
    if 'DNS' in wc.interface:
        result = netns_setdns(namespace=namespace_name, dns=wc.interface['DNS'])
        if result is not None:
            print(result)
    wireguard_config_set_route(interface_name, wc=wc, ipw=ipw, namespace=namespace_name)
    return None


