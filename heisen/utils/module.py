import imp

from heisen.core.log import logger


def load_module(module_name, module_path, handle_exception=True):
    file = None
    module = None
    try:
        file, pathname, desc = imp.find_module(module_name, [module_path])
        module = imp.load_module(module_name, file, pathname, desc)
    except Exception as e:
        if file is not None:
            file.close()

        if handle_exception:
            logger.exception(e)
        else:
            raise

    return module
