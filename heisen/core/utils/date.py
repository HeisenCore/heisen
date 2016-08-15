# coding: utf-8
import datetime
import calendar


def translate_ago_date(_date):

    now = datetime.datetime.now()
    diff = (now - _date)
    sec = int(diff.total_seconds())

    end_month = calendar.monthrange(now.year, now.month)[1]

    if sec <= 59:
        result = int(sec), 'seconds'

    elif 60 <= sec <= 3599:
        result = int(sec / 60), 'minutes'

    elif 3600 <= sec <= 86399:
        result = int(sec / 3600), 'hours'

    elif sec >= 86400:
        if diff.days <= 6:
            result = diff.days, 'days'

        elif 7 <= diff.days <= end_month:
            result = (diff.days / 7), 'weeks'

        elif (end_month + 1) <= diff.days <= 365:
            result = (diff.days / end_month), 'months'

        elif diff.days >= 366:
            result = (diff.days / 365), 'years'

    return result


def last_persian_date(_date):
    _tuple = translate_ago_date(_date)

    translate = {
        'seconds': 'ثانیه',
        'minutes': 'دقیقه',
        'hours': 'ساعت',
        'weeks': 'هفته',
        'days': 'روز',
        'months': 'ماه',
        'years': 'سال'
    }

    text = "{0} {1} پیش".format(_tuple[0], translate[_tuple[1]])

    return text


def epoch_to_stamp(_time):
    stamp = datetime.datetime.fromtimestamp(
        _time
    ).strftime('%Y-%m-%d %H:%M:%S')

    return stamp
