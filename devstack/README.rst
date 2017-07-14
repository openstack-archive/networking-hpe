==================================================================
Enabling Networking-hpe Baremetal Network Provisioning in Devstack
==================================================================

1. Download DevStack

2. Add this repo as an external repository for Baremetal network provisoning (BNP)::

    > cat local.conf
    [[local|localrc]]
    enable_plugin networking-hpe https://git.openstack.org/openstack/networking-hpe
    enable_service networking-hpe-plugin

3. Add the following required flag in local.conf to enable BNP ML2 MechanismDriver::

    Q_ML2_PLUGIN_MECHANISM_DRIVERS=openvswitch,l2population,hpe_bnp

4. Add the following required flag in local.conf to enable BNP Extension driver::

    #append the below lines
    Q_ML2_PLUGIN_EXT_DRIVERS=port_security,bnp_ext_driver,bnp_cred_ext_driver,bnp_switch_ports_ext_driver

5. Read the settings file for more details.

6. run ``stack.sh``
