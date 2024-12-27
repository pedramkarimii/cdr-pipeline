from django.core.management.base import BaseCommand
from apps.cdr.tasks.tasks_consumer import RabbitMQConsumer
from apps.core import os_setting_elastic
import time


class Command(BaseCommand):
    """ This class defines a Django management command to start the RabbitMQ consumer for processing CDRs. """

    help = 'Start the RabbitMQ consumer to process CDRs'

    def add_arguments(self, parser):
        """
        This method adds command-line arguments that can be passed when running the management command.
        Arguments include settings for queue prefix, shard count, RabbitMQ connection details, etc.
        """
        parser.add_argument(
            '--queue_prefix',
            type=str,
            default='cdr_queue',
            help='Prefix for the queue name.',
        )
        parser.add_argument(
            '--shard_count',
            type=int,
            default=4,
            help='Number of shards (queues) to consume from.',
        )
        parser.add_argument(
            '--host',
            type=str,
            default='localhost',
            help='RabbitMQ server host.',
        )
        parser.add_argument(
            '--port',
            type=int,
            default=5672,
            help='RabbitMQ server port.',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='guest',
            help='RabbitMQ username.',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='guest',
            help='RabbitMQ password.',
        )

    def handle(self, *args, **options):
        """
        This method handles the logic for starting the RabbitMQ consumer.
        It connects to the RabbitMQ server, starts consuming from the queues,
        and handles errors or manual interruption gracefully.
        """
        queue_prefix = options['queue_prefix']
        shard_count = options['shard_count']
        host = options['host']
        port = options['port']
        username = options['username']
        password = options['password']

        self.stdout.write(f"Starting RabbitMQ consumer with queue prefix '{queue_prefix}' and {shard_count} shards...")

        # Initialize and connect the consumer
        consumer = RabbitMQConsumer(
            queue_prefix=queue_prefix,
            shard_count=shard_count,
            host=host,
            port=port,
            username=username,
            password=password
        )

        try:
            consumer.connect()
            consumer.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write('Consumer stopped by user.')
        except Exception as e:
            self.stdout.write(f"Error occurred while consuming: {str(e)}")
        finally:
            consumer.close_connection()
            self.stdout.write('RabbitMQ consumer stopped and connection closed.')
