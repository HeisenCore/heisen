import inspect
import pprint
import traceback
import sys


def format(exc_info=None):
    if exc_info is None:
        _type, value, tback = sys.exc_info()
        traceback_text = ''.join(traceback.format_exception(_type, value, tback))
    else:
        _type, value, tback, traceback_text = exc_info

    while tback and tback.tb_next:
        tback = tback.tb_next

    local_vars = get_locals(tback)
    extra_info = get_info(value, tback)

    text = local_vars + traceback_text

    return text, extra_info


def get_locals(tback):
    try:
        if not tback:
            raise ValueError('Traceback is empty')

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
    traceback_obj = inspect.getframeinfo(tback)
    exception = value

    return {
        'exception_type': exception.__class__.__name__,
        'exception_message': str(exception),
        'exception_filename': traceback_obj.filename,
        'exception_function': traceback_obj.function,
        'exception_line': traceback_obj.lineno,
    }
