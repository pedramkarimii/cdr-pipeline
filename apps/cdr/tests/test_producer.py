import unittest
from unittest.mock import MagicMock, patch
import pika
import json
from datetime import datetime

from apps.cdr.tasks.tasks_producer import RabbitMQProducer


class TestRabbitMQProducer(unittest.TestCase):
    """
    This is the test class for testing the RabbitMQProducer.
    It will test the message publishing to the appropriate queue and retry logic.
    """

    def setUp(self):
        """Set up the test environment."""
        self.queue_prefix = 'cdr_queue'
        self.shard_count = 3
        self.rabbitmq_producer = RabbitMQProducer(
            queue_prefix=self.queue_prefix,
            shard_count=self.shard_count,
            url='amqps://user:password@localhost:5672/test'
        )
        self.rabbitmq_producer.channel = MagicMock()

    @patch('pika.BlockingConnection')
    def test_publish_message_success(self, mock_connection):
        """Test successful message publishing."""
        mock_connection.return_value.channel.return_value = self.rabbitmq_producer.channel

        message = {
            'src_number': '09120000001',
            'dest_number': '09120000002',
            'call_duration': 100,
            'call_successful': True,
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'timestamp': datetime.now().isoformat()
        }

        shard_id = self.rabbitmq_producer._get_shard_id(message['src_number'])
        expected_queue_name = f"{self.queue_prefix}_{shard_id}"

        self.rabbitmq_producer.publish_message(message)

        self.rabbitmq_producer.channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key=expected_queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Test published message to {expected_queue_name}: {message}")

    @patch('pika.BlockingConnection')
    def test_publish_message_retry_logic(self, mock_connection):
        """Test retry logic when publishing fails."""
        mock_connection.return_value.channel.return_value = self.rabbitmq_producer.channel

        message = {
            'src_number': '09120000001',
            'dest_number': '09120000002',
            'call_duration': 100,
            'call_successful': True,
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'timestamp': datetime.now().isoformat()
        }

        self.rabbitmq_producer.channel.basic_publish = MagicMock(side_effect=pika.exceptions.AMQPConnectionError)
        self.rabbitmq_producer.publish_message(message)
        self.assertEqual(self.rabbitmq_producer.channel.basic_publish.call_count, self.rabbitmq_producer.max_retries)
        print(f"Test retry logic triggered {self.rabbitmq_producer.max_retries} times.")

    @patch('pika.BlockingConnection')
    def test_publish_message_exceeds_max_retries(self, mock_connection):
        """Test when maximum retries are exceeded."""
        mock_connection.return_value.channel.return_value = self.rabbitmq_producer.channel

        message = {
            'src_number': '09120000001',
            'dest_number': '09120000002',
            'call_duration': 100,
            'call_successful': True,
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'timestamp': datetime.now().isoformat()
        }

        self.rabbitmq_producer.channel.basic_publish = MagicMock(side_effect=pika.exceptions.AMQPConnectionError)

        self.rabbitmq_producer.publish_message(message)

        self.assertEqual(self.rabbitmq_producer.channel.basic_publish.call_count, self.rabbitmq_producer.max_retries)
        print(
            f"Test exceeded max retries, failed to publish message after {self.rabbitmq_producer.max_retries} attempts.")
