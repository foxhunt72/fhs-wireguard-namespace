# network create wireguard interface

from .ip_wrapper import ip_wrapper, Ip_Wrapper_Command_Error

def wireguard_create(interface_name):
    """Create a wireguard interface."""
    # if check_namespace_name(namespace) is False:
    #     return "ERROR: Namespace name is not valid"
    # if check_namespace_exists(namespace) is True:
    #     return "ERROR: Namespace already exists"
    ipw = ip_wrapper()
    try:
        ipw.link_add_wireguard(interface_name)
    except Ip_Wrapper_Command_Error as e:
        if 'Operation not permitted' in str(e):
            return "ERROR: Permission denied, please run as root or with sudo"
        if 'File exists' in str(e):
            return f"ERROR: Interface {interface_name} allready exists"
        return "ERROR: " + str(e)
    return None


def move_interface_to_namespace(
    interface_name,
    namespace_name,
):
    """Move interface to namespace."""
    print(f"moving interface {interface_name} to namespace {namespace_name}")
    ipw = ip_wrapper()
    try:
        result = ipw.link_show_interface(interface_name)
    except Ip_Wrapper_Command_Error as e:
        if 'does not exist.' in str(e):
            return f"ERROR: Interface {interface_name} doesn't exist"
        return "ERROR: " + str(e)

    try:
        result = ipw.link_set_netns(interface_name, namespace_name)
    except Ip_Wrapper_Command_Error as e:
        if 'Invalid "netns" value' in str(e):
            return f"ERROR: namespace {namespace_name} doesn't exist"
        if 'Operation not permitted' in str(e):
            return "ERROR: Permission denied, please run as root or with sudo"
        return "ERROR: " + str(e)

    return None

def wireguard_check_exists(interface_name, namespace_name):
    """Check if wireguard interface is configured in namespace."""
    ipw = ip_wrapper()
    try:
        result = ipw.link_show_interface(interface_name)
    except Ip_Wrapper_Command_Error as e:
        if 'does not exist.' in str(e):
            return False
        return "ERROR: " + str(e)
    return True

