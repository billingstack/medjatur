from oslo.config import cfg


from fakturo.core import provider

from medjatur.plugin import DestinationPlugin
from medjatur import exceptions


cfg.CONF.register_opts([
    cfg.StrOpt('api_url', default='http://localhost:6543/v1'),
    cfg.StrOpt('account_id', help='Billingstack Merchant ID'),
    cfg.StrOpt('driver', default='billingstack')
], group='destination:fakturo')


class FakturoDestination(DestinationPlugin):
    __plugin_name__ = 'fakturo'
    """
    A destination that uses Fakturo as a client
    """
    def start(self):
        if not cfg.CONF[self.name].account_id:
            raise exceptions.ConfigurationError('Account ID not configured.')

        # NOTE: Get the underlying provider driver
        cls = provider.get_provider(cfg.CONF[self.name].driver)
        self.client = cls.get_client(cfg.CONF[self.name].api_url)

    def get_accounts(self):
        accounts = self.client.customer.list(
            account_id=cfg.CONF[self.name].account_id)
        return [a['id'] for a in accounts]

    def send_data(self, data):
        pass
