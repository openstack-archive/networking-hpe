# Copyright (c) 2015 OpenStack Foundation.
# Copyright (c) 2015 Hewlett-Packard Enterprise Development, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutron_lib.db import model_base
import sqlalchemy as sa


class BNPPhysicalSwitch(model_base.BASEV2, model_base.HasId):
    """Define physical switch properties."""
    __tablename__ = "bnp_physical_switches"
    name = sa.Column(sa.String(36), nullable=False)
    vendor = sa.Column(sa.String(16), nullable=False)
    family = sa.Column(sa.String(16), nullable=True)
    ip_address = sa.Column(sa.String(64), nullable=False)
    mac_address = sa.Column(sa.String(32), nullable=True)
    port_provisioning = sa.Column(sa.String(16), nullable=False)
    management_protocol = sa.Column(sa.String(16), nullable=False)
    credentials = sa.Column(sa.String(36), nullable=False)
    validation_result = sa.Column(sa.String(255), nullable=True)
    __table_args__ = (sa.PrimaryKeyConstraint('id'),
                      sa.UniqueConstraint('ip_address', 'mac_address'))


class BNPSwitchPortMapping(model_base.BASEV2):
    """Define neutron port and switch port mapping."""
    __tablename__ = "bnp_switch_port_mappings"
    neutron_port_id = sa.Column(sa.String(36), nullable=False)
    switch_port_name = sa.Column(sa.String(255), nullable=False)
    switch_id = sa.Column(sa.String(255), nullable=False)
    ifindex = sa.Column(sa.String(36), nullable=False)
    __table_args__ = (sa.PrimaryKeyConstraint('neutron_port_id'),)
    sa.ForeignKeyConstraint(['switch_id'],
                            ['bnp_physical_switches.id'],
                            ondelete='CASCADE')


class BNPNeutronPort(model_base.BASEV2):
    """Define neutron port properties."""
    __tablename__ = "bnp_neutron_ports"
    neutron_port_id = sa.Column(sa.String(36), nullable=False)
    lag_id = sa.Column(sa.String(36), nullable=True)
    access_type = sa.Column(sa.String(16), nullable=False)
    segmentation_id = sa.Column(sa.Integer, nullable=False)
    bind_status = sa.Column(sa.Boolean(), nullable=True)
    __table_args__ = (sa.PrimaryKeyConstraint('neutron_port_id'),)
    sa.ForeignKeyConstraint(['neutron_port_id'],
                            ['bnp_switch_port_mappings.neutron_port_id'],
                            ondelete='CASCADE')


class BNPSNMPCredential(model_base.BASEV2, model_base.HasId):
    """Define snmp credentials."""
    __tablename__ = "bnp_snmp_credentials"
    name = sa.Column(sa.String(36), nullable=False)
    protocol_type = sa.Column(sa.String(255), nullable=False)
    write_community = sa.Column(sa.String(255), nullable=True)
    security_name = sa.Column(sa.String(255), nullable=True)
    auth_protocol = sa.Column(sa.String(16), nullable=True)
    auth_key = sa.Column(sa.String(255), nullable=True)
    priv_protocol = sa.Column(sa.String(16), nullable=True)
    priv_key = sa.Column(sa.String(255), nullable=True)
    security_level = sa.Column(sa.String(16), nullable=True)
    __table_args__ = (sa.PrimaryKeyConstraint('id'),)


class BNPNETCONFCredential(model_base.BASEV2, model_base.HasId):
    """Define netconf credentials."""
    __tablename__ = "bnp_netconf_credentials"
    name = sa.Column(sa.String(36), nullable=False)
    protocol_type = sa.Column(sa.String(255), nullable=False)
    user_name = sa.Column(sa.String(255), nullable=True)
    password = sa.Column(sa.String(255), nullable=True)
    key_path = sa.Column(sa.String(255), nullable=True)
    __table_args__ = (sa.PrimaryKeyConstraint('id'),)
