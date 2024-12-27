import time
from django.core.management.base import BaseCommand
from apps.cdr.tasks.tasks_producer import RabbitMQProducer, generate_cdr
from apps.cdr.tasks.tasks_consumer import RabbitMQConsumer

""" run python manage.py create_producer_consumer --num_messages 500 --queue_prefix cdr_queue --shard_count 2 --host
 localhost --port 5672 --username guest --password guest
"""


class Command(BaseCommand):
    help = 'Create Producer and Consumer for RabbitMQ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_messages',
            type=int,
            default=500,
            help='Number of CDRs to send by the producer.',
        )
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
        # Retrieve command arguments
        num_messages = options['num_messages']
        queue_prefix = options['queue_prefix']
        shard_count = options['shard_count']
        host = options['host']
        port = options['port']
        username = options['username']
        password = options['password']

        # Run the producer process first
        self.stdout.write(f"Starting the producer to send {num_messages} messages to RabbitMQ...")
        self._run_producer(num_messages, queue_prefix, shard_count, host, port, username, password)

        # After the producer finishes or is interrupted, start the consumer
        self.stdout.write(f"Starting the consumer to process messages from RabbitMQ...")
        self._run_consumer(queue_prefix, shard_count, host, port, username, password)

    def _run_producer(self, num_messages, queue_prefix, shard_count, host, port, username, password):
        """
        Run the producer to publish messages to RabbitMQ.
        """
        producer = RabbitMQProducer(queue_prefix=queue_prefix, shard_count=shard_count, host=host, port=port,
                                    username=username, password=password)
        producer.connect()

        message_count = 0
        start_time = time.time()

        try:
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

    def _run_consumer(self, queue_prefix, shard_count, host, port, username, password):
        """
        Run the consumer to process messages from RabbitMQ.
        """
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
