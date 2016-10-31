import inspect
import pprint
import traceback
import sys


def format(exc_info=None):
    if exc_info is None:
        _type, value, tback = sys.exc_info()
    else:
        _type, value, tback, traceback_text = exc_info

    text = get_locals(tback)

    if tback is not None:
        text += ''.join(traceback.format_exception(_type, value, tback))
    else:
        text += traceback_text

    extra_info = get_info(value, tback)

    return text, extra_info


def get_locals(tback):
    try:
        if not tback:
            raise ValueError('Traceback is empty')

        while tback.tb_next:
            tback = tback.tb_next

        frame_locals = tback.tb_frame.f_locals
        for var in tback.tb_frame.f_locals.keys():
            if var.startswith('__'):
                frame_locals.pop(var)

        text = 'Locals: {}\n'.format(pprint.pformat(frame_locals))
    except Exception:
        print('Error in getting frame variables')
        traceback.print_exc()
        text = ''

    return text


def get_info(value, tback):
    info = {}

    exception = value
    info['exception_type'] = exception.__class__.__name__
    info['exception_message'] = str(exception)

    while tback and tback.tb_next:
        tback = tback.tb_next

    traceback_obj = inspect.getframeinfo(tback)

    info['exception_filename'] = traceback_obj.filename
    info['exception_function'] = traceback_obj.function
    info['exception_line'] = traceback_obj.lineno

    return info
