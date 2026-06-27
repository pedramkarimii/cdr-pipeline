from django.core.management.base import BaseCommand, CommandError

from apps.cdr.tasks.tasks_consumer import RabbitMQConsumer


class Command(BaseCommand):
    help = "Start the RabbitMQ CDR consumer."

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue-prefix",
            default="cdr_queue",
            help="RabbitMQ queue prefix.",
        )
        parser.add_argument(
            "--shard-count",
            type=int,
            default=2,
            help="Number of queue shards to consume.",
        )

    def handle(self, *args, **options):
        shard_count = options["shard_count"]
        if shard_count < 1:
            raise CommandError("--shard-count must be at least 1.")

        consumer = RabbitMQConsumer(
            queue_prefix=options["queue_prefix"],
            shard_count=shard_count,
        )

        if not consumer.connect():
            raise CommandError("Could not connect to RabbitMQ.")

        self.stdout.write(
            self.style.SUCCESS(
                f"Consuming {shard_count} RabbitMQ shard(s). Press Ctrl+C to stop."
            )
        )

        try:
            consumer.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write("Consumer stopped.")
        finally:
            consumer.close_connection()
