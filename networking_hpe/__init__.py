# -*- coding: utf-8 -*-

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

import gettext

from debtcollector import removals
import pbr.version
import six


__version__ = pbr.version.VersionInfo(
    'networking_hpe').version_string()


if six.PY2:
    gettext.install('networking_hpe', unicode=1)
else:
    gettext.install('networking_hpe')


# flake8: noqa
six.moves.builtins.__dict__['_'] = removals.remove(
    message='Builtin _ translation function is deprecated in OpenStack; '
            'use the function from _i18n module for your project.')(_)
