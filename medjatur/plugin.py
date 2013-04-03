# Copyright 2012 Bouvet ASA
#
# Author: Endre Karlson <endre.karlson@bouvet.no>
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
from stevedore import driver
from medjatur.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class Plugin(object):
    __plugin_ns__ = None

    __plugin_name__ = None
    __plugin_type__ = None

    def __init__(self):
        self.name = self.get_canonical_name()
        LOG.debug("Loaded plugin %s", self.name)

    def is_enabled(self):
        """
        Is this Plugin enabled?

        :retval: Boolean
        """
        return True

    @classmethod
    def get_plugin(cls, name, ns=None, invoke_on_load=False,
                   invoke_args=(), invoke_kwds={}):
        """
        Load a plugin from namespace
        """
        ns = ns or cls.__plugin_ns__
        if ns is None:
            raise RuntimeError('No namespace provided or __plugin_ns__ unset')

        LOG.debug('Looking for plugin %s in %s', name, ns)
        mgr = driver.DriverManager(ns, name)

        return mgr.driver(*invoke_args, **invoke_kwds) if invoke_on_load \
            else mgr.driver

    @classmethod
    def get_canonical_name(cls):
        """
        Return the plugin name
        """
        type_ = cls.get_plugin_type()
        name = cls.get_plugin_name()
        return "%s:%s" % (type_, name)

    @classmethod
    def get_plugin_name(cls):
        return cls.__plugin_name__

    @classmethod
    def get_plugin_type(cls):
        return cls.__plugin_type__

    def start(self):
        """
        Start this plugin
        """

    def stop(self):
        """
        Stop this plugin from doing anything
        """


class SyncPlugin(Plugin):
    def __init__(self, service):
        super(SyncPlugin, self).__init__()
        self.service = service


class SourcePlugin(SyncPlugin):
    """Plugin that fetches data at a Source."""
    __plugin_ns__ = 'medjatur.source'
    __plugin_type__ = 'source'

    def get_account_usages(self, account_id):
        """
        Get data from a source

        This should return a hash of projects with their usage data

        {'
            'account_id': [{}]
        '}
        """
        raise NotImplementedError


class DestinationPlugin(SyncPlugin):
    """Plugin that sends data to the remote side."""
    __plugin_ns__ = 'medjatur.destination'
    __plugin_type__ = 'destination'

    def get_accounts(self):
        """
        Return the billable accounts for the destination
        """
        raise NotImplementedError

    def send_data(self, data):
        """
        Send the billable data (usages) over to the billing system

        :param data: The data
        """
        raise NotImplementedError
