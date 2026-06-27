from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.cdr.models import Cdr


class CdrModelTest(TestCase):
    def setUp(self):
        self.valid_src_number = "09121234567"
        self.valid_dest_number = "09121234568"
        self.valid_call_duration = 120
        self.timestamp = timezone.now()
        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(
            seconds=self.valid_call_duration
        )

    def create_cdr(self, **overrides):
        values = {
            "src_number": self.valid_src_number,
            "dest_number": self.valid_dest_number,
            "call_duration": self.valid_call_duration,
            "timestamp": self.timestamp,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "call_successful": True,
        }
        values.update(overrides)
        return Cdr.objects.create(**values)

    def test_create_valid_cdr(self):
        cdr = self.create_cdr()
        self.assertEqual(cdr.src_number, self.valid_src_number)
        self.assertEqual(cdr.dest_number, self.valid_dest_number)
        self.assertEqual(cdr.call_duration, self.valid_call_duration)
        self.assertTrue(cdr.call_successful)

    def test_invalid_call_duration_fails_validation(self):
        cdr = Cdr(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=-10,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
        )
        with self.assertRaises(ValidationError):
            cdr.full_clean()

    def test_repeated_source_number_is_allowed(self):
        self.create_cdr()
        duplicate = self.create_cdr(dest_number="09121234569", call_successful=False)
        self.assertEqual(duplicate.src_number, self.valid_src_number)
        self.assertEqual(Cdr.objects.count(), 2)

    def test_repeated_destination_number_is_allowed(self):
        self.create_cdr()
        duplicate = self.create_cdr(src_number="09121234570", call_successful=False)
        self.assertEqual(duplicate.dest_number, self.valid_dest_number)
        self.assertEqual(Cdr.objects.count(), 2)

    def test_string_representation(self):
        cdr = self.create_cdr()
        expected = f"{self.valid_src_number} -> {self.valid_dest_number} | {self.valid_call_duration}s | Success"
        self.assertEqual(str(cdr), expected)

    def test_invalid_source_phone_number_fails_validation(self):
        cdr = Cdr(src_number="09121234", dest_number=self.valid_dest_number)
        with self.assertRaises(ValidationError):
            cdr.full_clean()

    def test_invalid_destination_phone_number_fails_validation(self):
        cdr = Cdr(src_number=self.valid_src_number, dest_number="09121234")
        with self.assertRaises(ValidationError):
            cdr.full_clean()

    def test_null_call_duration_is_allowed(self):
        cdr = self.create_cdr(call_duration=None)
        self.assertIsNone(cdr.call_duration)

    def test_indexes_exist(self):
        self.assertTrue(Cdr._meta.get_field("src_number").db_index)
        self.assertTrue(Cdr._meta.get_field("dest_number").db_index)
        self.assertTrue(Cdr._meta.get_field("timestamp").db_index)
        index_fields = [tuple(index.fields) for index in Cdr._meta.indexes]
        self.assertIn(("src_number", "dest_number", "timestamp"), index_fields)
