#!../bin/python
import sys
from json import dumps


usage = """
Options:\n\n[General options]:\n\n\n
 help                       Show this usage information.
                            for func help please send second arg
                            as a method name.
                            e.g:
                            ./manage.py help main.stop

 version                    Show version information

 runserver                  Start your server (For custom port, please
                            see settings file.)

 shutdown                   Shutdown your server

 start_component            Create your component. send your
                            component name as second argument.
                            e.g: python manage.py start_component test

 logs                       Show all logs(error, jobs, debug, object,
                            service, request)

 show_ras                   Show status of all raspberrys.

 plugin                     Show All components with their plugins.

 memory                     Access to all data of the shared memory.
                            Just pass your key to memory option.
                            e.g: python manage.py memory local_airports

 generate_settings          Generate your settings_local from scratch.
                            e.g: python manage.py generate_settings

 dump_filter                Create dump file (Filter.so) from user saved
                            filters on flight list.

 restore_filter             Restore saved dump file and apply to each
                            user on flight list.

"""


def main():

    if len(sys.argv) > 1:

        if sys.argv[1] == 'runserver':
            from services.rpc_core.run_rpc import runRPC
            runRPC()

        elif sys.argv[1] == 'start_component':
            from core.manager.execute_start_component import start_component

            # Create component
            start_component(sys.argv[2])

        elif sys.argv[1] == 'shutdown':
            from jsonrpclib import Server
            from socket import error
            from config.settings import CORE_PORT

            try:
                conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(CORE_PORT))
                conn.main.stop()

            except error:
                print 'Core Services shutdown \t\t\t\t\t\t[OK]'

        elif sys.argv[1] == 'show_ras':
            from jsonrpclib import Server
            from socket import error
            from config.settings import CORE_PORT

            try:
                conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(CORE_PORT))
                data = conn.raspberry.show_all_ras()
                pretty(data)

            except error:
                print 'Core Services shutdown \t\t\t\t\t\t[OK]'

        elif sys.argv[1] == 'command_ras':
            from jsonrpclib import Server
            from socket import error
            from core.db import cursor_local
            from config.settings import CORE_PORT

            try:

                conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(CORE_PORT))

                if len(sys.argv) == 4:
                    raspberries = [
                        cursor_local.raspberries.find_one(
                            {
                                'hostname': sys.argv[3],
                                'enabled': True
                            })['_id']
                    ]

                else:
                    raspberries = cursor_local.raspberries.distinct(
                                        '_id', {'enabled': True}
                                    )

                for raspberry in raspberries:
                    r = str(raspberry)
                    result = getattr(conn.raspberry, sys.argv[2])(r)
                    pretty(result)

                else:
                    print 'No raspberries'

            except error:
                print 'Core Services shutdown \t\t\t\t\t\t[OK]'

        elif sys.argv[1] == 'logs':
            from os import system
            from config.settings import CORE_ID

            system('tail -f /var/log/core/{0}/*'.format(CORE_ID))

        elif sys.argv[1] == 'memory':
            from jsonrpclib import Server
            from socket import error
            from config.settings import CORE_PORT

            try:
                key = sys.argv[2]
                conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(CORE_PORT))
                data = conn.main.access_shared_memory(key)
                pretty(data)

            except error:
                print 'Core Services shutdown \t\t\t\t\t\t[OK]'

        elif sys.argv[1] == 'generate_settings':
            from shutil import copyfile
            from config.settings import BASE_DIR

            raw = BASE_DIR + '/config/settings_local.txt'
            gen = BASE_DIR + '/config/settings_local.py'

            copyfile(raw, gen)

        elif sys.argv[1] == 'dump_filter':
            from jsonrpclib import Server
            import shelve
            from config.settings import BASE_DIR
            from bson.json_util import loads
            from socket import error
            from config.settings import CORE_PORT

            try:
                store = shelve.open(BASE_DIR + '/cache/filters.so')
                conn = Server('http://localhost:{0}'.format(CORE_PORT))
                data = conn.main.access_shared_memory('flight_list_filter')
                data = loads(data)
                store['data'] = data
                store.close()
                print "Dump \t\t\t\t\t\t[OK]"

            except error:
                print 'Core Services shutdown \t\t\t\t\t\t[OK]'

        elif sys.argv[1] == 'restore_filter':
            from socket import error
            from jsonrpclib import Server
            from config.settings import CORE_PORT

            try:
                conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(CORE_PORT))
                conn.jobs.restore_filters()
                print "Restore \t\t\t\t\t\t[OK]"

            except error:
                print 'Core Services shutdown \t\t\t\t\t\t[OK]'

        elif sys.argv[1] == 'plugin':
            from jsonrpclib import Server
            from socket import error
            from config.settings import CORE_PORT

            try:
                conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(CORE_PORT))
                data = conn.listMethods()
                pretty(dumps(data))

            except error:
                print 'Core Services shutdown \t\t\t\t\t\t[OK]'

        elif sys.argv[1] == 'help':

            if len(sys.argv) == 3:
                from os import system
                from jsonrpclib import Server
                from socket import error
                from config.settings import CORE_PORT

                try:
                    conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTilocalhost:{0}'.format(CORE_PORT))
                    data = conn.methodHelp(sys.argv[2])
                    system('echo {}'.format(data))

                except error:
                    print 'Core Services shutdown \t\t\t\t\t\t[OK]'

            elif len(sys.argv) == 2:
                print usage


def pretty(data):
    from os import system

    try:
        import pjson

    except ImportError:
        print "Please install pjson module. \t( sudo pip install pjson )"
        return

    system("""echo '{0}' | pjson""".format(data))


if __name__ == "__main__":
    # execute only if run as a script
    main()
