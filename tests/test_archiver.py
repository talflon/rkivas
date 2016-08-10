import os.path
from argparse import ArgumentParser
from unittest.mock import Mock

import rkivas.config
from rkivas import Archiver


def load_config(config_map, tmpdir):
    config_filename = os.path.join(str(tmpdir), 'ini')
    with open(config_filename, 'w') as config_file:
        for header, body in config_map.items():
            print('[' + header + ']', file=config_file)
            for k, v in body.items():
                print('{} = {}'.format(k, v), file=config_file)
    parser = ArgumentParser()
    rkivas.config.add_default_opts(parser)
    opts = parser.parse_args(['--config-file', config_filename])
    return rkivas.config.load_config_files(opts)


def test_get_ext(tmpdir):
    ext_map = {
        'jpeg': 'jpg',
        'htm': 'html',
    }
    cfg = load_config({'extension-map': ext_map}, tmpdir)
    archiver = Archiver(cfg)
    assert archiver.get_ext('a/b/c/whatever.png') == 'png'
    assert archiver.get_ext('stuff.tar') == 'tar'
    assert archiver.get_ext('blah.jpeg') == 'jpg'
    assert archiver.get_ext('bleh.jpg') == 'jpg'
    assert archiver.get_ext('jkl/x123.htm') == 'html'
    assert archiver.get_ext('jkl/x123.html') == 'html'


def test_get_timestamp_ext_dispatch(tmpdir):
    ext = 'blah'
    handler_name = 'bleh'
    path = 'any/thin.g'
    result = 'yay'
    cfg = load_config({
        'extension-handlers': {
            ext: handler_name,
        },
    }, tmpdir)
    archiver = Archiver(cfg)
    archiver.get_timestamp_bleh = Mock()
    archiver.get_timestamp_bleh.return_value = result
    assert archiver.get_timestamp(ext, path) == result
    archiver.get_timestamp_bleh.assert_called_once_with(path)
