# rkivas file backupper
# Copyright (C) 2016  Daniel Getz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import logging.config
import sys
from configparser import RawConfigParser
from io import StringIO


DEFAULT_CONFIG_FILE = '/etc/rkivas.conf'

DEFAULTS = """
[sources]

[backup]
filename-format = {source}/{timestamp:%Y-%m}/{source}-{timestamp:%Y%m%d_%H%M%S}-{hash}
hash-algorithm = md5
hash-length = 8

[backup-no-timestamp]
filename-format = {source}/unknown/{source}-{hash}
hash-algorithm = md5
hash-length = 16

[extension-map]
jpeg = jpg
tiff = tif

[extension-handlers]
jpg = exif
tif = exif
"""


def load_config_files(opts):
    cfg = RawConfigParser()
    cfg.read_file(StringIO(DEFAULTS))
    cfg.read(opts.config_file)
    return cfg


def add_default_opts(parser):
    parser.add_argument(
        '--config-file', default=DEFAULT_CONFIG_FILE,
        help='load a particular configuration file',
        metavar='FILE')
    parser.add_argument(
        '-L', '--logging',
        choices=['DEBUG', 'WARN', 'WARNING', 'INFO', 'ERROR',
                 'CRITICAL', 'FATAL'],
        help='log to stderr with the given LEVEL', metavar='LEVEL')
    parser.add_argument(
        '--debug-config', action='store_true',
        help='instead of running, output the combined configuration')


def config_logging(opts, cfg):
    if opts.logging:
        level = getattr(logging, opts.logging)
        logging.basicConfig(
            level=level,
            format='%(asctime)s %(levelname)s %(name)s - %(message)s',
        )
    elif (cfg.has_section('formatters') or
            cfg.has_section('handlers') or
            cfg.has_section('loggers') or
            cfg.has_section('logger_root')):
        tmp = StringIO()
        cfg.write(tmp)
        tmp.seek(0)
        logging.config.fileConfig(tmp, disable_existing_loggers=False)
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format='%(levelname)s %(name)s - %(message)s',
        )
    if hasattr(logging, 'captureWarnings'):
        logging.captureWarnings(True)


def load_opts_into_cfg(opts, cfg, which):
    for section, options in which.items():
        for cfg_key, opt_key in options.items():
            value = getattr(opts, opt_key, None)
            if value is not None:
                cfg.set(section, cfg_key, str(value))


def load_common_config(opts):
    cfg = load_config_files(opts)
    if not opts.debug_config:
        config_logging(opts, cfg)
    return cfg


def load_config(opts, opts_spec=None):
    cfg = load_common_config(opts)
    if opts_spec:
        load_opts_into_cfg(opts, cfg, opts_spec)
    if opts.debug_config:
        cfg.write(sys.stdout)
        sys.exit(0)
    return cfg
