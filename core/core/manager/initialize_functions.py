from core import toLog
from config.settings import AIRPORT_CODE as c
from config.settings import archive_interval_time as a
from config.settings import flight_list_jobs as f
from services.rpc_core.query_handler import send_request


def initial_executer():
    # Flight list jobs
    flight_list_jobs = send_request('jobs.flight_list_jobs', (f, ))
    msg = "Start flight list jobs cycle: {}"
    toLog(msg.format(flight_list_jobs), 'jobs')

    # Departure Archive balacing round
    ori_archive = send_request('jobs.archive', ('origins', c, a))
    msg = "Start Archive Origins round cycle: {}"
    toLog(msg.format(ori_archive), 'jobs')

    # Arrival Archive balacing round
    des_archive = send_request('jobs.archive', ('destinations', c, a))
    msg = "Start Archive Destinations round cycle: {}"
    toLog(msg.format(des_archive), 'jobs')

    # Arrival Archive balacing round
    run_raspberry = send_request('raspberry.run_raspberry', '')
    msg = "Start Raspberry cycle: {}"
    toLog(msg.format(run_raspberry), 'jobs')

    check_alive = send_request('jobs.check_alive_core', (5, ))
    msg = "Start check_alive_core cycle: {}"
    toLog(msg.format(check_alive), 'jobs')

    pa_audio = send_request('jobs.play_pa_audio', '')
    weather = send_request('jobs.weather', (5, ))
    run_emergency_or_ads = send_request('jobs.run_emergency_or_ads', (1, ))
    restart_not_availables = send_request('jobs.restart_not_availables', (1, ))
    check_playlists_expiry = send_request('jobs.check_playlists_expiry', (60, ))
