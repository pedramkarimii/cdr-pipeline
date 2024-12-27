from django.core.management.base import BaseCommand
import time

from apps.cdr.tasks.tasks_producer import RabbitMQProducer, generate_cdr


class Command(BaseCommand):
    """Django management command to send random CDRs to RabbitMQ."""
    help = 'Send random CDRs to RabbitMQ'

    def add_arguments(self, parser):
        """Define custom command arguments."""
        parser.add_argument(
            '--num_messages',
            type=int,
            default=500,
            help='Number of CDRs to send',
        )

    def handle(self, *args, **options):
        """Main execution method to send messages to RabbitMQ."""
        producer = RabbitMQProducer(queue_prefix='cdr_queue', shard_count=2)
        producer.connect()

        message_count = 0
        start_time = time.time()

        try:
            num_messages = options['num_messages']
            for _ in range(num_messages):
                cdr = generate_cdr()
                producer.publish_message(cdr)
                message_count += 1

                if message_count % 100 == 0:
                    elapsed_time = time.time() - start_time
                    self.stdout.write(f"Sent {message_count} messages. Time taken: {elapsed_time:.2f} seconds.")
                    time.sleep(0.22)
        except KeyboardInterrupt:
            self.stdout.write(f"Process interrupted. {message_count} messages sent.")
        finally:
            producer.close_connection()
            elapsed_time = time.time() - start_time
            self.stdout.write(f"Total messages sent: {message_count}. Time taken: {elapsed_time:.2f} seconds.")
