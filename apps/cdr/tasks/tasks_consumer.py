import json
import logging

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.cdr.models import Cdr
from apps.cdr.tasks.tasks_main import RabbitMQMain


logger = logging.getLogger(__name__)


class RabbitMQConsumer(RabbitMQMain):
    def connect(self) -> bool:
        if not super().connect():
            return False

        for shard_id in range(self.shard_count):
            self.channel.basic_consume(
                queue=f"{self.queue_prefix}_{shard_id}",
                on_message_callback=self.process_message,
                auto_ack=False,
            )
        return True

    def process_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            cdr_data = self._parse_message(message)
            self._save_cdr(cdr_data)
        except (TypeError, ValueError, KeyError) as exc:
            logger.warning("Discarding invalid CDR message: %s", exc)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        except Exception:
            logger.exception("CDR persistence failed; message will be retried.")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Processed CDR from %s", cdr_data["src_number"])

    def _parse_datetime(self, value):
        parsed = parse_datetime(value)
        if parsed is None:
            raise ValueError("Invalid ISO-8601 datetime.")

        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.get_current_timezone())

        return parsed

    def _parse_message(self, message: dict) -> dict:
        required = {
            "src_number",
            "dest_number",
            "call_duration",
            "call_successful",
            "timestamp",
        }
        missing = sorted(required.difference(message))
        if missing:
            raise ValueError(
                "Missing required CDR fields: {}".format(", ".join(missing))
            )

        if not isinstance(message["call_successful"], bool):
            raise ValueError("call_successful must be a boolean.")

        return {
            "src_number": message["src_number"],
            "dest_number": message["dest_number"],
            "call_duration": message["call_duration"],
            "call_successful": message["call_successful"],
            "timestamp": self._parse_datetime(message["timestamp"]),
            "start_time": self._parse_datetime(
                message.get("start_time", message["timestamp"])
            ),
            "end_time": self._parse_datetime(
                message.get("end_time", message["timestamp"])
            ),
        }

    def _save_cdr(self, cdr_data: dict) -> None:
        cdr = Cdr(**cdr_data)
        cdr.full_clean()
        cdr.save()

    def start_consuming(self) -> None:
        if self.channel is None:
            raise RuntimeError("RabbitMQ channel is not connected.")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Consumer interrupted.")
        finally:
            self.close_connection()
