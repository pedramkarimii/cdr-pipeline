from time import sleep
import pika
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Django command to pause execution until RabbitMQ is available.
    This command ensures the application does not proceed until RabbitMQ is up and running.
    """

    def handle(self, *args, **options):
        self.stdout.write('Waiting for RabbitMQ ...')

        rabbitmq_connection = None
        while not rabbitmq_connection:
            try:
                rabbitmq_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host='rabbitmq'
                    )
                )
            except pika.exceptions.AMQPConnectionError:
                self.stdout.write('RabbitMQ unavailable, Retrying ...')
                sleep(1)
            else:
                rabbitmq_connection.close()

        self.stdout.write(self.style.SUCCESS('RabbitMQ available'))
