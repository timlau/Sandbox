#!/usr/bin/python

import argparse
import sys
from subprocess import call


def setup_parser():
    parser = argparse.ArgumentParser(description='two-way sync of locale and remote dir (ssh)')
    parser.add_argument('--host', help='remote ssh host to sync with')
    parser.add_argument('--params', help='parameters to rsync', default='vaurP')
    parser.add_argument('local_dir', help='local directory to sync')
    parser.add_argument('remote_dir', help='remote dir to sync')
    return parser

parser = setup_parser()
args = parser.parse_args(sys.argv[1:])
params = args.__dict__ # Get a dict from Namespace
SYNC_LOCAL = 'rsync -e ssh -%(params)s %(local_dir)s/ %(host)s:%(remote_dir)s' % params
SYNC_REMOTE = 'rsync -e ssh -%(params)s %(host)s:%(remote_dir)s/ %(local_dir)s' % params
print('***** Creating remote dir')
call('ssh %(host)s mkdir -p %(remote_dir)s ' % params, shell=True)
print('***** Syncronize %(local_dir)s -> %(host)s:%(remote_dir)s' % params)
call(SYNC_LOCAL, shell=True)
print('***** Syncronize %(host)s:%(remote_dir)s -> %(local_dir)s' % params)
call(SYNC_REMOTE, shell=True)

