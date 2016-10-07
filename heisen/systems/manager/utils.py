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


def write_config(prefix, application):
    supervisor_config = '/etc/supervisor/conf.d/'
    config_parser = ConfigParser.RawConfigParser()

    config_parser.add_section(application.section_name())
    for option, value in sorted(application.configs().items()):
        config_parser.set(application.section_name(), option, value)

    config_parser.remove_option(application.section_name(), 'name')

    with open('{}{}'.format(supervisor_config, application.config_filename()), 'w') as configfile:
        supervisor_config,
        configfile.write('# Auto generated file, Don\'t edit.\n')
        config_parser.write(configfile)

    print('Created config file for {} in {}{}'.format(
        application.name, supervisor_config, application.config_filename()
    ))
