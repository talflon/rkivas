import os
import os.path
from argparse import ArgumentParser
from unittest.mock import Mock, call

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


def test_get_ext_different_case(tmpdir):
    ext_map = {
        'jpeg': 'jpg',
        'htm': 'html',
    }
    cfg = load_config({'extension-map': ext_map}, tmpdir)
    archiver = Archiver(cfg)
    assert archiver.get_ext('a/b/c/whatever.PNG') == 'png'
    assert archiver.get_ext('stuff.Tar') == 'tar'
    assert archiver.get_ext('blah.Jpeg') == 'jpg'
    assert archiver.get_ext('bleh.JPG') == 'jpg'
    assert archiver.get_ext('jkl/x123.HTM') == 'html'
    assert archiver.get_ext('jkl/x123.hTmL') == 'html'


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


def check_archive_all(files, sources, tmpdir):
    source_map = {os.path.join(str(tmpdir), k): v for k, v in sources.items()}
    expected_calls = []
    for p, names in files.items():
        dir = os.path.join(str(tmpdir), p)
        os.mkdir(dir)
        for n in names:
            file_path = os.path.join(dir, n)
            expected_calls.append(call(sources[p], file_path))
            with open(file_path, 'w') as f:
                f.write('stuff')
    cfg = load_config({'sources': source_map}, tmpdir)
    archiver = Archiver(cfg)
    archiver.archive_file = Mock()
    archiver.archive_all()
    archiver.archive_file.assert_has_calls(expected_calls, any_order=True)


def test_archive_all(tmpdir):
    check_archive_all(files={
        'path1': ['abc', 'def'],
        'path2': ['a', 'b', 'c'],
    }, sources={
        'path1': 'source1',
        'path2': 'source2',
    }, tmpdir=tmpdir)


def test_archive_all_mixed_cases(tmpdir):
    check_archive_all(files={
        'path1': ['abc', 'DEF'],
        'Path2': ['a', 'B', 'c'],
    }, sources={
        'path1': 'Source1',
        'Path2': 'source2',
    }, tmpdir=tmpdir)
