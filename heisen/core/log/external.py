from heisen.config import settings


def graylog(name, logger, formatter):
    try:
        import graypy

        if name not in getattr(settings, 'EXTERNAL_LOGGERS', []):
            return

        graylog_config = getattr(settings, 'GRAYLOG', {})
        handler = graypy.GELFHandler(**graylog_config)

        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except ImportError:
        pass
