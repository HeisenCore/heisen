import imp

from heisen.core.log import logger

def load_module(module_name, module_path):
    file = None
    module = None
    try:
        file, pathname, desc = imp.find_module(module_name, [module_path])
        module = imp.load_module(module_name, file, pathname, desc)
    except Exception as e:
        logger.exception(e)
        if file is not None:
            file.close()

    return module
