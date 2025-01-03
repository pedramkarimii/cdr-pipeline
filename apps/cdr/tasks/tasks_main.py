import time
from apps.core import os_setting_elastic  # noqa
import random
from datetime import datetime, timedelta
import pika
# import subprocess


class RabbitMQMain:
    """
    This is the base class that provides the basic connection and queue declaration logic for both
     producers and consumers.
    It includes methods to connect to RabbitMQ, declare queues, and close the connection.
    """

    _instance = None

    def __new__(cls, queue_prefix, shard_count,  # noqa
                url='amqps://pdtwxisb:JSRKhYIwoER7i99A1BjqP1CRQstZvTr7@possum.lmq.cloudamqp.com/pdtwxisb',
                host='localhost', port=5672, username='guest',
                password='guest', virtual_host='/', max_retries=5, retry_delay=2):
        """
        The `__new__` method ensures that only one instance of the class is created.
        :param queue_prefix: Prefix for naming queues.
        :param shard_count: Number of shards (partitions) in the system.
        :param url: The URL for the RabbitMQ broker (optional, used when connecting to cloud-based brokers).
        :param host: The RabbitMQ server's hostname.
        :param port: The port to connect to RabbitMQ.
        :param username: The username for authentication.
        :param password: The password for authentication.
        :param virtual_host: The virtual host to connect to (used for logical separation).
        :param max_retries: The maximum number of retries if a connection fails.
        :param retry_delay: The delay between retries (in seconds).
        """
        if not cls._instance:  # Check if an instance already exists
            cls._instance = super(RabbitMQMain, cls).__new__(cls)  # Create the instance if it doesn't exist
            # Initialize the instance variables
            cls._instance.queue_prefix = queue_prefix
            cls._instance.shard_count = shard_count
            cls._instance.max_retries = max_retries
            cls._instance.retry_delay = retry_delay
            cls._instance.url = url
            cls._instance.host = host
            cls._instance.port = port
            cls._instance.username = username
            cls._instance.password = password
            cls._instance.virtual_host = virtual_host
            cls._instance.connection = None
            cls._instance.channel = None
        return cls._instance

    def connect(self):
        """Establish connection to RabbitMQ."""
        credentials = pika.PlainCredentials(self.username, self.password)
        attempt = 0

        while attempt < self.max_retries:
            try:
                self.connection = pika.BlockingConnection(  # noqa
                    pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        credentials=credentials,
                        virtual_host=self.virtual_host
                    )
                )
                self.channel = self.connection.channel()  # noqa

                for shard_id in range(self.shard_count):  # noqa
                    queue_name = f"{self.queue_prefix}_{shard_id}"
                    self.channel.queue_declare(queue=queue_name, durable=True)

                print(f"Connected to RabbitMQ at {self.host}:{self.port} and consuming messages...")
                break

            except pika.exceptions.AMQPConnectionError as e:
                attempt += 1
                print(f"Connection attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Max retry attempts reached. Connection failed.")
            finally:
                if attempt >= self.max_retries:
                    print("Connection retries exhausted. Please check RabbitMQ server.")

    def close_connection(self):
        """Close the RabbitMQ connection safely."""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                print("Connection closed successfully.")
            else:
                print("Connection is already closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")


def generate_cdr():
    """Generate a random Call Detail Record (CDR)"""
    src_number = f"0912{random.randint(1000000, 9999999)}"
    dest_number = f"0912{random.randint(1000000, 9999999)}"
    call_duration = random.randint(1, 60000)
    call_successful = random.choice([True, False])
    start_time = (datetime.now() - timedelta(seconds=random.randint(0, 8640000000))).isoformat()
    end_time = (datetime.now() - timedelta(seconds=random.randint(0, 8640000000))).isoformat()
    timestamp = (datetime.now() - timedelta(seconds=random.randint(0, 8640000000))).isoformat()

    return {
        "src_number": src_number,
        "dest_number": dest_number,
        "call_duration": call_duration,
        "call_successful": call_successful,
        "start_time": start_time,
        "end_time": end_time,
        "timestamp": timestamp
    }

# You can Run with command: python manage.py create_producer_consumer --queue_prefix cdr_queue --shard_count 2
# Or remove the comments from lines (6 and 123...140).

# if __name__ == "__main__":
#     # 1. The producer process (`tasks_producer.py`) is responsible for generating tasks or data.
#     # 2. The consumer processes (`tasks_consumer.py`) process the tasks, each assigned a unique shard ID.
#     producer_process = subprocess.Popen(['python', 'tasks_producer.py'])
#     consumer_processes = []
#     shard_count = 2
#     for shard_id in range(shard_count):
#         process = subprocess.Popen(['python', 'tasks_consumer.py', str(shard_id)])
#         consumer_processes.append(process)
#     try:
#         producer_process.wait()
#         for process in consumer_processes:
#             process.wait()
#     except KeyboardInterrupt:
#         producer_process.terminate()
#         for process in consumer_processes:
#             process.terminate()
#         print("Shutting down gracefully.")
