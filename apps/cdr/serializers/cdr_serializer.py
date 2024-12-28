from rest_framework import serializers
from apps.cdr.models import Cdr
from apps.core import validators


class CdrSearchSerializer(serializers.ModelSerializer):
    """
    Serializer for validating and serializing Call Detail Records (CDR) for search purposes.

    This serializer ensures that incoming data used for filtering and searching CDRs is properly validated.
    It includes fields for filtering by source number, destination number, call duration, timestamps,
    and success status.
    """

    class Meta:
        model = Cdr
        fields = ['src_number', 'dest_number', 'call_duration', 'start_time', 'end_time', 'timestamp',
                  'call_successful']
        read_only_fields = ['src_number', 'dest_number', 'call_duration', 'start_time', 'end_time',
                            'timestamp', 'call_successful']

        extra_kwargs = {
            'src_number': {
                'required': True,
                'validators': [validators.PhoneNumberMobileValidator()],
                'error_messages': {
                    'required': 'The src number field is required.',
                    'invalid': 'The src number field must be a valid phone number.',
                },
            },
            'dest_number': {
                'required': True,
                'validators': [validators.PhoneNumberMobileValidator()],
                'error_messages': {
                    'required': 'The dest number field is required.',
                    'invalid': 'The dest number field must be a valid phone number.',
                },
            },
            'call_duration': {
                'required': True,
                'error_messages': {
                    'required': 'The call duration field is required.',
                    'invalid': 'The call duration field must be a positive integer.',
                },
            },
            'start_time': {
                'required': True,
                'error_messages': {
                    'required': 'The start time field is required.',
                    'invalid': 'The start time field must be a valid datetime.',
                },
            },
            'end_time': {
                'required': True,
                'error_messages': {
                    'required': 'The end time field is required.',
                    'invalid': 'The end time field must be a valid datetime.',
                },
            },
            'timestamp': {
                'required': True,
                'error_messages': {
                    'required': 'The timestamp field is required.',
                    'invalid': 'The timestamp field must be a valid datetime.',
                },
            },
            'call_successful': {
                'required': True,
                'error_messages': {
                    'required': 'The call successful field is required.',
                    'invalid': 'The call successful field must be a boolean.',
                },
            },
        }
