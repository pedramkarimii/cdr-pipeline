import unittest
from _pydatetime import timedelta
from unittest.mock import MagicMock, patch
import pika
from datetime import datetime

from apps.cdr.tasks.tasks_main import RabbitMQMain, generate_cdr


class TestRabbitMQMain(unittest.TestCase):

    def setUp(self):
        """Setup the test environment for RabbitMQMain class."""
        self.queue_prefix = 'cdr_queue'
        self.shard_count = 2
        self.rabbitmq = RabbitMQMain(
            queue_prefix=self.queue_prefix,
            shard_count=self.shard_count,
            url='amqps://user:password@localhost:5672/test'
        )
        self.rabbitmq.connection = MagicMock()
        self.rabbitmq.channel = MagicMock()

    @patch('pika.BlockingConnection')
    def test_connect_success(self, MockConnection):
        """Test that RabbitMQ connection is established successfully."""
        mock_connection = MagicMock()
        MockConnection.return_value = mock_connection
        self.rabbitmq.connect()

        self.assertIsNotNone(self.rabbitmq.connection)
        self.assertIsNotNone(self.rabbitmq.channel)

        for shard_id in range(self.shard_count):
            queue_name = f"{self.queue_prefix}_{shard_id}"
            self.rabbitmq.channel.queue_declare.assert_any_call(queue=queue_name, durable=True)

    @patch('pika.BlockingConnection')
    def test_connect_retry_on_failure(self, MockConnection):
        """Test that the connection retries on failure."""
        MockConnection.side_effect = pika.exceptions.AMQPConnectionError("Connection error")

        self.rabbitmq.connect()

        self.assertEqual(MockConnection.call_count, self.rabbitmq.max_retries)

    @patch('pika.BlockingConnection')
    def test_connect_max_retries_exceeded(self, MockConnection):
        """Test that the connection fails after max retries."""
        MockConnection.side_effect = pika.exceptions.AMQPConnectionError("Connection error")

        self.rabbitmq.connect()

        self.assertEqual(MockConnection.call_count, self.rabbitmq.max_retries)
        self.assertIsNone(self.rabbitmq.connection)
        self.assertIsNone(self.rabbitmq.channel)

    def test_close_connection_success(self):
        """Test that the connection closes successfully."""
        self.rabbitmq.connection.is_open = True
        self.rabbitmq.close_connection()

        self.rabbitmq.connection.close.assert_called_once()

    def test_close_connection_no_open_connection(self):
        """Test closing connection when there is no open connection."""
        self.rabbitmq.connection.is_open = False
        self.rabbitmq.close_connection()

        self.rabbitmq.connection.close.assert_not_called()

    def test_close_connection_error(self):
        """Test error when closing connection."""
        self.rabbitmq.connection.is_open = True
        self.rabbitmq.connection.close.side_effect = Exception("Connection close failed")

        with self.assertRaises(Exception):
            self.rabbitmq.close_connection()


class TestGenerateCDR(unittest.TestCase):

    def test_generate_cdr_structure(self):
        """Test that the generate_cdr function returns a dictionary with the correct keys."""
        cdr = generate_cdr()

        self.assertIn("src_number", cdr)
        self.assertIn("dest_number", cdr)
        self.assertIn("call_duration", cdr)
        self.assertIn("call_successful", cdr)
        self.assertIn("start_time", cdr)
        self.assertIn("end_time", cdr)
        self.assertIn("timestamp", cdr)

    def test_generate_cdr_random_values(self):
        """Test that the random values generated for CDR are within expected range."""
        cdr = generate_cdr()

        self.assertGreater(cdr["call_duration"], 0)

        self.assertTrue(cdr["src_number"].startswith("0912"))
        self.assertTrue(cdr["dest_number"].startswith("0912"))

        try:
            datetime.fromisoformat(cdr["start_time"])
            datetime.fromisoformat(cdr["end_time"])
            datetime.fromisoformat(cdr["timestamp"])
        except ValueError:
            self.fail("Generated CDR contains invalid ISO datetime format")

    def test_generate_cdr_timestamp(self):
        """Test that the timestamp is within the expected range (i.e., a recent timestamp)."""
        cdr = generate_cdr()

        timestamp = datetime.fromisoformat(cdr["timestamp"])

        self.assertTrue(abs(datetime.now() - timestamp) < timedelta(days=100).total_seconds())
