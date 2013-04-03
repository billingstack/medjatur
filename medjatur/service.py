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

    def _diff_lists(self, left, right):
        """
        Returns a list of items in the dst side presnt on the src side and
        missing ones
        """
        present = [i for i in right if i in left]
        missing = list(set(right) - set(left))
        return present, missing

    def _diff_map(self, left, right):
        """
        Returns a dict with what is present and missing on dst / src lists
        """
        return {
            'right_left': self._diff_lists(right, left),
            'left_right': self._diff_lists(left, right)
        }

    def periodic_tasks(self):
        """
        Runs the periodic sync of data.
        """
        left = self.source.get_accounts()
        right = self.destination.get_accounts()

        mapping = self._diff_map(left, right)

        accounts = mapping['left_right']

        for k, v in mapping.items():
            if len(v[1]) > 0:
                LOG.warning('Directions %s has %i missing accounts', k,
                            len(v[1]))

        # There are no valid accounts
        if len(accounts[0]) == 0:
            msg = 'No viable accounts found, missing:\n%s' % "."\
                .join(accounts[1])
            LOG.error(msg)
            return
