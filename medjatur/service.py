from oslo.config import cfg

from medjatur.openstack.common.service import Service
from medjatur.openstack.common import log

from medjatur.destination import get_destination
from medjatur.source import get_source


cfg.CONF.import_opt('state_path', 'medjatur.paths')

cfg.CONF.register_opts([
    cfg.IntOpt('interval', default=10),
    cfg.StrOpt('source', default='ceilometer'),
    cfg.StrOpt('destination', default='fakturo')
])

LOG = log.getLogger(__name__)


class MediatorService(Service):

    def __init__(self, *args, **kw):
        super(MediatorService, self).__init__(*args, **kw)

    def start(self):
        super(MediatorService, self).start()
        self.source = get_source(
            cfg.CONF.source, invoke_args=(self,), invoke_on_load=True)
        self.source.start()

        self.destination = get_destination(
            cfg.CONF.destination, invoke_args=(self,), invoke_on_load=True)
        self.destination.start()

        self.tg.add_timer(cfg.CONF.interval, self.periodic_tasks)

    def periodic_tasks(self):
        LOG.debug('Syncing data')
        self.destination.get_accounts()
