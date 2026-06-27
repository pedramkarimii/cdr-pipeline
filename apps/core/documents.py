from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from apps.cdr.models import Cdr


@registry.register_document
class CdrDocument(Document):
    class Index:
        name = "cdrs"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Cdr
        fields = [
            "src_number",
            "dest_number",
            "call_duration",
            "start_time",
            "end_time",
            "timestamp",
            "call_successful",
        ]
