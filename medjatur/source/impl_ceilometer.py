import os

from oslo.config import cfg
from keystoneclient.v2_0 import client as ksclient
from ceilometerclient import client as ceilometerclient

from medjatur.plugin import SourcePlugin
from medjatur.openstack.common import log
from medjatur import exceptions


LOG = log.getLogger(__name__)

cfg.CONF.register_opts([
    cfg.StrOpt('insecure', default=True),
    cfg.StrOpt('timeout', default=600),
    cfg.StrOpt('ceilometer_url'),
    cfg.StrOpt('ca_file'),
    cfg.StrOpt('cert_file'),
    cfg.StrOpt('key_file'),
    cfg.StrOpt('os_username', default=os.environ.get('OS_USERNAME')),
    cfg.StrOpt('os_password', default=os.environ.get('OS_PASSWORD')),
    cfg.StrOpt('os_tenant_id', default=os.environ.get('OS_TENANT_ID')),
    cfg.StrOpt('os_tenant_name', default=os.environ.get('OS_TENANT_NAME')),
    cfg.StrOpt('os_service_type', default=os.environ.get('OS_SERVICE_TYPE')),
    cfg.StrOpt('os_endpoint_type', default=os.environ.get('OS_ENDPOINT_TYPE')),
    cfg.StrOpt('os_auth_token', default=os.environ.get('OS_AUTH_TOKEN')),
    cfg.StrOpt('os_auth_url', default=os.environ.get('OS_AUTH_URL'))],
    group='source:ceilometer'
)


class CeilometerSource(SourcePlugin):
    __plugin_name__ = 'ceilometer'

    def start(self):
        self.client = self._get_client()

    def _get_ksclient(self, **kwargs):
        """Get an endpoint and auth token from Keystone.

        :param username: name of user
        :param password: user's password
        :param tenant_id: unique identifier of tenant
        :param tenant_name: name of tenant
        :param auth_url: endpoint to authenticate against
        """
        return ksclient.Client(username=kwargs.get('username'),
                               password=kwargs.get('password'),
                               tenant_id=kwargs.get('tenant_id'),
                               tenant_name=kwargs.get('tenant_name'),
                               auth_url=kwargs.get('auth_url'),
                               insecure=kwargs.get('insecure'))

    def _get_endpoint(self, client, **kwargs):
        """Get an endpoint using the provided keystone client."""
        return client.service_catalog.url_for(
            service_type=kwargs.get('service_type') or 'metering',
            endpoint_type=kwargs.get('endpoint_type') or 'publicURL')

    def _get_client(self):
        opts = cfg.CONF[self.name]

        if opts.os_auth_token and opts.ceilometer_url:
            token = opts.os_auth_token
            endpoint = opts.ceilometer_url
        elif opts.os_username and opts.os_password and opts.os_auth_url \
                and (opts.os_tenant_name or opts.os_tenant_id):
            auth_opts = {
                'username': opts.os_username,
                'password': opts.os_password,
                'tenant_id': opts.os_tenant_id,
                'tenant_name': opts.os_tenant_name,
                'auth_url': opts.os_auth_url,
                'service_type': opts.os_service_type,
                'endpoint_type': opts.os_endpoint_type,
                'insecure': opts.insecure
            }
            _ksclient = self._get_ksclient(**auth_opts)
            token = opts.os_auth_token or _ksclient.auth_token

            endpoint = opts.ceilometer_url or \
                self._get_endpoint(_ksclient, **auth_opts)
        elif opts.ceilometer_url:
            endpoint = opts.ceilometer_url
        else:
            raise exceptions.ConfigurationError('Please check config.')

        kwargs = {
            'token': token,
            'insecure': opts.insecure,
            'timeout': opts.timeout,
            'ca_file': opts.ca_file,
            'cert_file': opts.cert_file,
            'key_file': opts.key_file,
        }

        client = ceilometerclient.Client('2', endpoint, **kwargs)
        return client

    def get_accounts(self, account_id):
        LOG.debug("Fetching ceilometer data for %s" % account_id)
        for account in self.ceilometer.project.list():
            print account
