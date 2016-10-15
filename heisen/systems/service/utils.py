import os
import sys
import ConfigParser


def check_user():
    if os.geteuid() == 0:
        print('You\'re running script as root, run it as normal user')
        sys.exit(1)


def change_ownership():
    conf_dir = '/etc/supervisor/conf.d'
    if os.getuid() != os.stat(conf_dir).st_uid:
        print('You\'re not owner of supervisor config dir, changing ownership')
        os.system('sudo chown -R $USER. {}'.format(conf_dir))
