import os
import re
import time

from oslo.config import cfg

from medjatur.openstack.common import log


LOG = log.getLogger(__name__)


def find_config(config_path):
    """
    Find a configuration file using the given hint.

    Code nabbed from cinder.

    :param config_path: Full or relative path to the config.
    :returns: List of config paths
    """
    possible_locations = [
        config_path,
        os.path.join(cfg.CONF.state_path, "etc", "medjatur", config_path),
        os.path.join(cfg.CONF.state_path, "etc", config_path),
        os.path.join(cfg.CONF.state_path, config_path),
        "/etc/medjatur/%s" % config_path,
    ]

    found_locations = []

    for path in possible_locations:
        LOG.debug('Searching for configuration at path: %s' % path)
        if os.path.exists(path):
            LOG.debug('Found configuration at path: %s' % path)
            found_locations.append(os.path.abspath(path))

    return found_locations


def read_config(prog, argv):
    config_files = find_config('%s.conf' % prog)

    cfg.CONF(argv[1:], project='medjatur', prog=prog,
             default_config_files=config_files)


def capital_to_underscore(string):
    return "_".join(l.lower() for l in re.findall('[A-Z][^A-Z]*',
                                                  string))


def underscore_to_capital(string):
    return ''.join(x.capitalize() or '_' for x in string.split('_'))


def get_item_properties(item, fields, mixed_case_fields=[], formatters={}):
    """Return a tuple containing the item properties.

    :param item: a single item resource (e.g. Server, Tenant, etc)
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
        to format the values
    """
    row = []

    for field in fields:
        if field in formatters:
            row.append(formatters[field](item))
        else:
            if field in mixed_case_fields:
                field_name = field.replace(' ', '_')
            else:
                field_name = field.lower().replace(' ', '_')
            if not hasattr(item, field_name) and \
                    (isinstance(item, dict) and field_name in item):
                data = item[field_name]
            else:
                data = getattr(item, field_name, '')
            if data is None:
                data = ''
            row.append(data)
    return tuple(row)


def get_columns(data):
    """
    Some row's might have variable count of columns, ensure that we have the
    same.

    :param data: Results in [{}, {]}]
    """
    columns = set()

    def _seen(col):
        columns.add(str(col))

    map(lambda item: map(_seen, item.keys()), data)
    return list(columns)


def unixtime(dt_obj):
    """Format datetime object as unix timestamp

    :param dt_obj: datetime.datetime object
    :returns: float

    """
    return time.mktime(dt_obj.utctimetuple())
