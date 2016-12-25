from heisen.core.db.mongodb import MongoDatabases
from heisen.config import settings


db = MongoDatabases()

el = None
try:
    from elasticsearch import Elasticsearch
    el = Elasticsearch(
        settings.ELASTICSEARCH_CONNECTIONS,
        **settings.ELASTICSEARCH_CONFIGS
    )
except ImportError as e:
    pass
