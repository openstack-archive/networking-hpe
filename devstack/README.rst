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

5. Provide the extra config file in local.conf for loading mechanism driver::

    Q_PLUGIN_EXTRA_CONF_PATH=/etc/neutron/plugins/ml2
    Q_PLUGIN_EXTRA_CONF_FILES=(ml2_conf_hpe.ini)

6. Read the settings file for more details.

7. run ``stack.sh``



#############
# ----------
# Local.conf
# ----------
# [[local|localrc]]
# RECLONE=no
# 
# GIT_BASE=https://git.openstack.org
# DATABASE_PASSWORD=ccdemo11
# RABBIT_PASSWORD=ccdemo11
# SERVICE_PASSWORD=ccdemo11
# ADMIN_PASSWORD=ccdemo11
# MYSQL_PASSWORD=ccdemo11
# 
# DEST=/opt/stack
# LOGFILE=$DEST/logs/stack.sh.log
# LOGDAYS=1
# 
# disable_service horizon
# 
# # Networking-hpe devstack setup
# enable_plugin  networking-hpe  file:///opt/stack/networking-hpe
# enable_service networking-hpe-plugin
# 
# Q_ML2_PLUGIN_MECHANISM_DRIVERS=openvswitch,l2population,hpe_bnp
# Q_ML2_PLUGIN_EXT_DRIVERS=port_security,bnp_ext_driver,bnp_cred_ext_driver,bnp_switch_ports_ext_drivers
# Q_PLUGIN_EXTRA_CONF_PATH=/etc/neutron/plugins/ml2
# Q_PLUGIN_EXTRA_CONF_FILES=(ml2_conf_hpe.ini)
