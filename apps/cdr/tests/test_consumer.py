import unittest
from unittest.mock import MagicMock, patch
import json
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import pika
from apps.cdr.tasks.tasks_consumer import RabbitMQConsumer


class TestRabbitMQConsumer(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.queue_prefix = 'cdr_queue'
        self.shard_count = 3
        self.rabbitmq_consumer = RabbitMQConsumer(
            queue_prefix=self.queue_prefix,
            shard_count=self.shard_count,
            url='amqps://user:password@localhost:5672/test'
        )
        self.rabbitmq_consumer.channel = MagicMock()

    @patch('pika.BlockingConnection')
    def test_connect_success(self, MockConnection):
        """Test successful connection to RabbitMQ."""
        mock_connection = MagicMock()
        MockConnection.return_value = mock_connection
        self.rabbitmq_consumer.connect()

        self.assertIsNotNone(self.rabbitmq_consumer.connection)
        self.assertIsNotNone(self.rabbitmq_consumer.channel)

        MockConnection.assert_called_once_with(
            pika.ConnectionParameters(
                host=self.rabbitmq_consumer.host,
                port=self.rabbitmq_consumer.port,
                credentials=pika.PlainCredentials(self.rabbitmq_consumer.username, self.rabbitmq_consumer.password),
                virtual_host=self.rabbitmq_consumer.virtual_host
            )
        )

    @patch('pika.BlockingConnection')
    def test_connect_retry_on_failure(self, MockConnection):
        """Test the retry mechanism when RabbitMQ connection fails."""
        MockConnection.side_effect = pika.exceptions.AMQPConnectionError("Connection error")

        self.rabbitmq_consumer.connect()
        self.assertEqual(MockConnection.call_count, self.rabbitmq_consumer.max_retries)

    def test_process_message_valid(self):
        """Test valid message processing and saving to the database."""
        valid_message = {
            "src_number": "09121234567",
            "dest_number": "09129876543",
            "call_duration": 120,
            "call_successful": True,
            "start_time": "2025-01-02T23:59:57.189903",
            "end_time": "2025-01-02T23:59:57.189917",
            "timestamp": "2025-01-02T23:59:57.189920"
        }

        with patch.object(self.rabbitmq_consumer, '_save_cdr') as mock_save_cdr:
            self.rabbitmq_consumer.process_message(MagicMock(), MagicMock(), MagicMock(), json.dumps(valid_message))
            mock_save_cdr.assert_called_once()

            saved_cdr = mock_save_cdr.call_args[0][0]
            parsed_timestamp = parse_datetime(valid_message['timestamp'])
            self.assertEqual(saved_cdr['timestamp'], parsed_timestamp.replace(tzinfo=timezone.get_current_timezone()))

    def test_process_message_empty(self):
        """Test processing of an empty message."""
        empty_message = {}

        with patch.object(self.rabbitmq_consumer, '_save_cdr') as mock_save_cdr:
            self.rabbitmq_consumer.process_message(MagicMock(), MagicMock(), MagicMock(), json.dumps(empty_message))

            mock_save_cdr.assert_not_called()

    @patch.object(RabbitMQConsumer, '_save_cdr')
    def test_process_message_corrupted_json(self, mock_save_cdr):
        """Test handling of a corrupted (malformed) JSON message."""
        corrupted_message = "{'src_number': '09121234567', 'dest_number': '09129876543'"

        self.rabbitmq_consumer.process_message(MagicMock(), MagicMock(), MagicMock(), corrupted_message)
        mock_save_cdr.assert_not_called()

    def test_process_message_non_json(self):
        """Test handling of non-JSON messages."""
        non_json_message = "This is not a JSON message."

        with patch.object(self.rabbitmq_consumer, '_save_cdr') as mock_save_cdr:
            self.rabbitmq_consumer.process_message(MagicMock(), MagicMock(), MagicMock(), non_json_message)
            mock_save_cdr.assert_not_called()

    @patch.object(RabbitMQConsumer, '_save_cdr')
    def test_save_cdr(self, mock_save_cdr):
        """Test the database saving logic for CDR."""
        cdr_data = {
            'src_number': '09121234567',
            'dest_number': '09129876543',
            'call_duration': 120,
            'call_successful': True,
            'timestamp': timezone.now(),
            'start_time': timezone.now(),
            'end_time': timezone.now(),
        }

        self.rabbitmq_consumer._save_cdr(cdr_data)
        mock_save_cdr.assert_called_once_with(cdr_data)

    def test_message_parsing_timestamp(self):
        """Test parsing and timezone conversion of timestamp fields."""
        message = {
            'src_number': '09121234567',
            'dest_number': '09129876543',
            'call_duration': 100,
            'call_successful': True,
            'timestamp': "2025-01-02T23:59:57.189920",
            'start_time': "2025-01-02T23:59:57.189903",
            'end_time': "2025-01-02T23:59:57.189917"
        }

        cdr_data = self.rabbitmq_consumer._parse_message(message)

        self.assertTrue(cdr_data['timestamp'].tzinfo is not None)
        self.assertTrue(cdr_data['start_time'].tzinfo is not None)
        self.assertTrue(cdr_data['end_time'].tzinfo is not None)

    @patch.object(RabbitMQConsumer, '_save_cdr')
    def test_multiple_shards(self, mock_save_cdr):
        """Test processing across multiple shards."""
        valid_message = {
            "src_number": "09121234567",
            "dest_number": "09129876543",
            "call_duration": 120,
            "call_successful": True,
            "start_time": "2025-01-02T23:59:57.189903",
            "end_time": "2025-01-02T23:59:57.189917",
            "timestamp": "2025-01-02T23:59:57.189920"
        }

        for shard_id in range(self.shard_count):
            self.rabbitmq_consumer.process_message(MagicMock(), MagicMock(), MagicMock(), json.dumps(valid_message))

        self.assertEqual(mock_save_cdr.call_count, self.shard_count)
