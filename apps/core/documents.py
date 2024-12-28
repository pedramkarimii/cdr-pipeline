from elasticsearch import Elasticsearch
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from apps.cdr.models import Cdr
from elasticsearch.helpers import bulk
import random
from datetime import datetime, timedelta

es = Elasticsearch([{'scheme': 'http', 'host': 'localhost', 'port': 9200}])


@registry.register_document
class CdrDocument(Document):
    """CdrDocument is a class that defines how CDR (Call Data Record) data should be indexed
    and stored in Elasticsearch."""

    class Index:
        """Define settings for the Elasticsearch index."""
        name = 'cdrs'
        settings = {
            'number_of_shards': 2,
            'number_of_replicas': 1
        }

    class Django:
        """Maps the Django model to the Elasticsearch document."""
        model = Cdr
        fields = [
            'src_number',
            'dest_number',
            'call_duration',
            'start_time',
            'end_time',
            'timestamp',
            'call_successful',
        ]

    class Meta:
        """Meta class for additional Elasticsearch settings and configurations."""
        doc_type = 'doc'
        auto_refresh = True
        related_models = [Cdr]
        queryset_pagination = 10000
        index = 'cdrs'
        index_settings = {'number_of_shards': 2, 'number_of_replicas': 1}
        index_analyzers = {
            'custom_analyzer': {
                'tokenizer': 'standard',
                'filter': ['lowercase', 'stop', 'snowball']
            }
        }

    @classmethod
    def bulk_index(cls, documents):
        """Bulk index the documents into Elasticsearch."""
        success, failed = bulk(es, documents, index="cdrs")
        print(f"Successfully indexed {success} documents.")
        if failed:
            print(f"Failed to index {failed} documents.")
