# Copyright 2015 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""bm network provisioning
Revision ID: 3297cd3f2323
Revises: start_bm_nw_provisioning
Create Date: 2015-07-06 00:25:06.980102
"""

# revision identifiers, used by Alembic.
revision = '3297cd3f2323'
down_revision = 'start_bm_nw_provisioning'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('bnp_physical_switches',
                    sa.Column('id', sa.String(36), nullable=False),
                    sa.Column('name', sa.String(36), nullable=False),
                    sa.Column('vendor', sa.String(16), nullable=False),
                    sa.Column('family', sa.String(16), nullable=True),
                    sa.Column('ip_address', sa.String(64), nullable=False),
                    sa.Column('mac_address', sa.String(32), nullable=True),
                    sa.Column('port_provisioning', sa.String(16),
                              nullable=False),
                    sa.Column('management_protocol', sa.String(16),
                              nullable=False),
                    sa.Column('credentials', sa.String(36), nullable=False),
                    sa.Column('validation_result', sa.String(255),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('ip_address', 'mac_address'))

    op.create_table('bnp_snmp_credentials',
                    sa.Column('id', sa.String(36), nullable=False),
                    sa.Column('name', sa.String(36), nullable=False),
                    sa.Column('protocol_type', sa.String(255), nullable=False),
                    sa.Column('write_community',
                              sa.String(255), nullable=True),
                    sa.Column('security_name', sa.String(255), nullable=True),
                    sa.Column('auth_protocol', sa.String(16), nullable=True),
                    sa.Column('auth_key', sa.String(255), nullable=True),
                    sa.Column('priv_protocol', sa.String(16), nullable=True),
                    sa.Column('priv_key', sa.String(255), nullable=True),
                    sa.Column('security_level', sa.String(16), nullable=True),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('bnp_netconf_credentials',
                    sa.Column('id', sa.String(36), nullable=False),
                    sa.Column('name', sa.String(36), nullable=False),
                    sa.Column('protocol_type', sa.String(255), nullable=False),
                    sa.Column('user_name', sa.String(255), nullable=True),
                    sa.Column('password', sa.String(255), nullable=True),
                    sa.Column('key_path', sa.String(255), nullable=True),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('bnp_switch_port_mappings',
                    sa.Column('neutron_port_id', sa.String(36),
                              nullable=False),
                    sa.Column('switch_port_name', sa.String(36),
                              nullable=False),
                    sa.Column('switch_id', sa.String(36), nullable=False),
                    sa.Column('ifindex', sa.String(36), nullable=False),
                    sa.PrimaryKeyConstraint('neutron_port_id'),
                    sa.ForeignKeyConstraint(
                        ['switch_id'],
                        ['bnp_physical_switches.id'],
                        ondelete='CASCADE'))

    op.create_table('bnp_neutron_ports',
                    sa.Column('neutron_port_id', sa.String(36),
                              nullable=False),
                    sa.Column('lag_id', sa.String(36), nullable=True),
                    sa.Column('access_type', sa.String(16), nullable=False),
                    sa.Column('segmentation_id', sa.Integer, nullable=False),
                    sa.Column('bind_status', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('neutron_port_id'),
                    sa.ForeignKeyConstraint(
                        ['neutron_port_id'],
                        ['bnp_switch_port_mappings.neutron_port_id'],
                        ondelete='CASCADE'))
