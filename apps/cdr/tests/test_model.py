from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from apps.cdr.models import Cdr

class CdrModelTest(TestCase):
    """
    Test case for the CDR model.
    """

    def setUp(self):
        """
        Setup for the tests. This method is automatically called before each test.
        """
        self.valid_src_number = "09121234567"
        self.valid_dest_number = "09121234568"
        self.valid_call_duration = 120
        self.invalid_call_duration = -10
        self.timestamp = timezone.now()

        # Set start_time and end_time as well
        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(seconds=self.valid_call_duration)

    def test_create_valid_cdr(self):
        """
        Test creating a CDR with valid data, including start_time and end_time.
        """
        cdr = Cdr.objects.create(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=self.valid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
            call_successful=True
        )

        self.assertEqual(cdr.src_number, self.valid_src_number)
        self.assertEqual(cdr.dest_number, self.valid_dest_number)
        self.assertEqual(cdr.call_duration, self.valid_call_duration)
        self.assertEqual(cdr.start_time, self.start_time)
        self.assertEqual(cdr.end_time, self.end_time)
        self.assertEqual(cdr.call_successful, True)

    def test_create_cdr_with_invalid_call_duration(self):
        """
        Test creating a CDR with invalid call duration (should raise a validation error).
        """
        cdr = Cdr(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=self.invalid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
        )

        with self.assertRaises(ValidationError):
            cdr.full_clean()

    def test_create_cdr_with_duplicate_src_number(self):
        """
        Test creating a CDR with duplicate source number (should raise an IntegrityError).
        """
        Cdr.objects.create(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=self.valid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
            call_successful=True
        )

        with self.assertRaises(IntegrityError):
            Cdr.objects.create(
                src_number=self.valid_src_number,
                dest_number="09121234569",
                call_duration=self.valid_call_duration,
                timestamp=self.timestamp,
                start_time=self.start_time,
                end_time=self.end_time,
                call_successful=False
            )

    def test_create_cdr_with_duplicate_dest_number(self):
        """
        Test creating a CDR with duplicate destination number (should raise an IntegrityError).
        """
        Cdr.objects.create(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=self.valid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
            call_successful=True
        )

        with self.assertRaises(IntegrityError):
            Cdr.objects.create(
                src_number="09121234570",
                dest_number=self.valid_dest_number,
                call_duration=self.valid_call_duration,
                timestamp=self.timestamp,
                start_time=self.start_time,
                end_time=self.end_time,
                call_successful=False
            )

    def test_string_representation(self):
        """
        Test the string representation of the CDR model.
        """
        cdr = Cdr.objects.create(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=self.valid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
            call_successful=True
        )

        expected_string = f'{self.valid_src_number} -> {self.valid_dest_number} | {self.valid_call_duration}s | Success'
        self.assertEqual(str(cdr), expected_string)

    def test_invalid_phone_number_format(self):
        """
        Test invalid source phone number using the custom phone number validator.
        """
        invalid_phone_number = "09121234"
        cdr = Cdr(
            src_number=invalid_phone_number,
            dest_number=self.valid_dest_number,
            call_duration=self.valid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
        )

        with self.assertRaises(ValidationError):
            cdr.full_clean()

    def test_invalid_phone_number_format_dest(self):
        """
        Test invalid destination phone number using the custom phone number validator.
        """
        invalid_phone_number = "09121234"
        cdr = Cdr(
            src_number=self.valid_src_number,
            dest_number=invalid_phone_number,
            call_duration=self.valid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
        )

        with self.assertRaises(ValidationError):
            cdr.full_clean()

    def test_create_cdr_with_valid_call_duration(self):
        """
        Test creating a CDR with valid call duration.
        """
        cdr = Cdr.objects.create(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=self.valid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
            call_successful=True
        )

        self.assertEqual(cdr.call_duration, self.valid_call_duration)

    def test_create_cdr_with_null_call_duration(self):
        """
        Test creating a CDR with null call duration (should be allowed as blank=True).
        """
        cdr = Cdr.objects.create(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=None,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
            call_successful=True
        )

        self.assertIsNone(cdr.call_duration)

    def test_indexing_on_fields(self):
        """
        Test that the database indexes on src_number, dest_number, and timestamp are created.
        """
        cdr = Cdr(
            src_number=self.valid_src_number,
            dest_number=self.valid_dest_number,
            call_duration=self.valid_call_duration,
            timestamp=self.timestamp,
            start_time=self.start_time,
            end_time=self.end_time,
            call_successful=True
        )
        cdr.save()

        indexes = Cdr._meta.indexes
        index_fields = [index.fields for index in indexes]

        # Check if there's an index on 'src_number', 'dest_number', and 'timestamp'
        self.assertTrue(any(
            set(['src_number', 'dest_number', 'timestamp']).issubset(fields)
            for fields in index_fields
        ))
