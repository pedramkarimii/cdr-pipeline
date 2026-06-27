from time import monotonic

from django.core.management.base import BaseCommand, CommandError

from apps.cdr.tasks.tasks_main import generate_cdr
from apps.cdr.tasks.tasks_producer import RabbitMQProducer


class Command(BaseCommand):
    help = "Publish generated CDR messages to RabbitMQ."

    def add_arguments(self, parser):
        parser.add_argument(
            "--num-messages",
            type=int,
            default=100,
            help="Number of CDR messages to publish.",
        )
        parser.add_argument(
            "--queue-prefix",
            default="cdr_queue",
            help="RabbitMQ queue prefix.",
        )
        parser.add_argument(
            "--shard-count",
            type=int,
            default=2,
            help="Number of queue shards.",
        )

    def handle(self, *args, **options):
        num_messages = options["num_messages"]
        shard_count = options["shard_count"]

        if num_messages < 1:
            raise CommandError("--num-messages must be at least 1.")
        if shard_count < 1:
            raise CommandError("--shard-count must be at least 1.")

        producer = RabbitMQProducer(
            queue_prefix=options["queue_prefix"],
            shard_count=shard_count,
        )

        if not producer.connect():
            raise CommandError("Could not connect to RabbitMQ.")

        started_at = monotonic()
        published = 0

        try:
            for _ in range(num_messages):
                if not producer.publish_message(generate_cdr()):
                    raise CommandError("Could not publish a CDR message.")
                published += 1
        finally:
            producer.close_connection()

        elapsed = monotonic() - started_at
        self.stdout.write(
            self.style.SUCCESS(
                f"Published {published} CDR messages in {elapsed:.2f} seconds."
            )
        )
