fhs_wireguard_namespace
=======================


Create a namespace with a wireguard interface for connectivity, wireguard interface is created in the current namespace and moved to the requested namespace, so the vpn uses the current namespace for connectivity to the vpn server.



Usage
-----

.. code-block:: bash

  fhs-wireguard-namespace wgquick-up-in-ns wg5 wgnamespace
  
This brings up wireguard interface wg5 using /etc/wireguard/wg5.conf 

Installation
------------
.. code-block:: bash

  python -m venv wg-venv
  source wg-venv/bin/activate

  git clone https://github.com/foxhunt72/fhs-wireguard-namespace.git
  cd fhs-wireguard-namespace
  pip install .

Requirements
^^^^^^^^^^^^
- /usr/bin/ip
- wireguard
- wireguard-tools


Compatibility
-------------
Linux only

Licence
-------
MIT Licence

Authors
-------

`fhs-wireguard-namespace` was written by `Richard de Vos <rdevos72@gmail.com>`_.
