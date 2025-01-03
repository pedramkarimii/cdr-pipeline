import time
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from apps.cdr.tasks.tasks_main import generate_cdr
from apps.cdr.tasks.tasks_producer import RabbitMQProducer
from apps.cdr.tasks.tasks_consumer import RabbitMQConsumer


class Command(BaseCommand):
    """
    Django management command to create and run both a RabbitMQ producer and consumer.

    This command sets up a producer that sends a specified number of CDR (Call Data Record)
    messages to RabbitMQ and a consumer that processes messages from multiple RabbitMQ queues.
    """

    help = 'Create Producer and Consumer for RabbitMQ'

    def add_arguments(self, parser):
        """
        Define the command-line arguments for this management command.

        Arguments:
        --num_messages  : Number of CDRs to send via the producer.
        --queue_prefix  : Prefix for the queue name.
        --shard_count   : Number of shards (queues) to consume from.
        --amqp_url      : AMQP URL for the RabbitMQ connection.
        """
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
            '--amqp_url',
            type=str,
            default='amqps://pdtwxisb:JSRKhYIwoER7i99A1BjqP1CRQstZvTr7@possum.lmq.cloudamqp.com/pdtwxisb',
            help='AMQP URL for RabbitMQ connection.',
        )

    def handle(self, *args, **options):
        """
        Entry point for the management command.

        This method reads the options (number of messages, queue prefix, shard count, and AMQP URL),
        and then starts both the producer and the consumer to interact with RabbitMQ.
        """
        num_messages = options['num_messages']
        queue_prefix = options['queue_prefix']
        shard_count = options['shard_count']
        amqp_url = options['amqp_url']

        parsed_url = urlparse(amqp_url)
        username = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port or 5672
        virtual_host = parsed_url.path.lstrip('/')

        self.stdout.write(f"Starting the producer to send {num_messages} messages to RabbitMQ...")
        self._run_producer(num_messages, queue_prefix, shard_count, host, port, username, password, virtual_host)

        self.stdout.write(f"Starting the consumer to process messages from RabbitMQ...")
        self._run_consumer(queue_prefix, shard_count, host, port, username, password, virtual_host)

    def _run_producer(self, num_messages, queue_prefix, shard_count, host, port, username, password, virtual_host):
        """
        Runs the RabbitMQ producer that sends messages to RabbitMQ.

        This method initializes the RabbitMQProducer instance, connects to RabbitMQ,
        and sends the specified number of CDR messages. The messages are generated using
        the `generate_cdr` function. The producer sends messages to the queues
        in a round-robin fashion based on the shard count.

        Args:
        - num_messages (int): The number of messages to send.
        - queue_prefix (str): The prefix for the queue names.
        - shard_count (int): The number of shards (queues) to distribute the messages across.
        - host (str): The RabbitMQ server hostname.
        - port (int): The RabbitMQ server port.
        - username (str): The RabbitMQ server username.
        - password (str): The RabbitMQ server password.
        - virtual_host (str): The RabbitMQ virtual host.
        """
        producer = RabbitMQProducer(
            queue_prefix=queue_prefix,
            shard_count=shard_count,
            host=host,
            port=port,
            username=username,
            password=password,
            virtual_host=virtual_host
        )
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

        except KeyboardInterrupt:
            self.stdout.write(f"Process interrupted. {message_count} messages sent.")

        finally:
            producer.close_connection()
            elapsed_time = time.time() - start_time
            self.stdout.write(f"Total messages sent: {message_count}. Time taken: {elapsed_time:.2f} seconds.")

    def _run_consumer(self, queue_prefix, shard_count, host, port, username, password, virtual_host):
        """
        Runs the RabbitMQ consumer that processes messages from RabbitMQ.

        This method initializes the RabbitMQConsumer instance, connects to RabbitMQ,
        and starts consuming messages from the queues. The consumer listens for messages
        on multiple queues based on the shard count, processes each message, and
        acknowledges the messages once they have been processed.

        Args:
        - queue_prefix (str): The prefix for the queue names.
        - shard_count (int): The number of shards (queues) to consume from.
        - host (str): The RabbitMQ server hostname.
        - port (int): The RabbitMQ server port.
        - username (str): The RabbitMQ server username.
        - password (str): The RabbitMQ server password.
        - virtual_host (str): The RabbitMQ virtual host.
        """
        consumer = RabbitMQConsumer(
            queue_prefix=queue_prefix,
            shard_count=shard_count,
            host=host,
            port=port,
            username=username,
            password=password,
            virtual_host=virtual_host
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
