import os
from os.path import join, exists
import sys

from heisen.config import settings


def check_user():
    if os.geteuid() == 0:
        print('You\'re running script as root, run it as normal user')
        sys.exit(1)


def change_ownership():
    conf_dir = '/etc/supervisor/conf.d'
    if os.getuid() != os.stat(conf_dir).st_uid:
        print('You\'re not owner of supervisor config dir, changing ownership')
        os.system('sudo chown -R $USER. {}'.format(conf_dir))


def is_virtualenv(path):
    virtualenv_dirs = ['bin', 'include', 'lib', 'local']
    is_virtualenv = all([
        exists(join(path, dir_name)) for dir_name in virtualenv_dirs
    ])

    if is_virtualenv:
        return join(path, 'bin')


def prompt(message, inputs='yn'):
    valid_input = False

    while not valid_input:
        input = raw_input(message).lower()

        if input not in inputs:
            print('Invalid input, try again')
        else:
            valid_input = True

    return True if input == 'y' else False


def find_virtualenv():
    path = None
    for method in [virtualenv_wrapper, virtualenv_parent, virtualenv_specified]:
        path = method()
        if path:
            return path

    print('Could not find virtualenv, using system path')


def virtualenv_wrapper():
    if not os.environ.get('WORKON_HOME', None):
        return

    if not prompt('Are you using virtualenv wrapper? (y/n) '):
        return

    workon_name = raw_input('Enter workon name: ')
    virtualenv_dir = join(os.environ['WORKON_HOME'], workon_name)
    return is_virtualenv(virtualenv_dir)


def virtualenv_parent():
    base_dir = getattr(settings, 'BASE_DIR', 'HEISEN_BASE_DIR')
    parent_dir = base_dir.rstrip('/').rpartition('/')[0]

    virtualenv_dir = is_virtualenv(parent_dir)

    if virtualenv_dir:
        return

    if not prompt('Detected a virtualenv on parent_dir, use it? (y/n) '):
        return

    return virtualenv_dir


def virtualenv_specified():
    if not prompt('Are you using virtualenv? (Y/n) '):
        return

    virtualenv_dir = raw_input('Enter virtualenv path: ')
    return is_virtualenv(virtualenv_dir)
