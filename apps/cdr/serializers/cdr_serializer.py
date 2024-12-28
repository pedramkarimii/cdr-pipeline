from rest_framework import serializers
from apps.core import validators


class CdrSearchSerializer(serializers.Serializer):
    """
    Serializer for validating Call Detail Records (CDR) search parameters.
    """
    src_number = serializers.CharField(
        required=False,
        validators=[validators.PhoneNumberMobileValidator()],
        error_messages={
            "invalid": "The src number field must be a valid phone number.",
        },
    )
    dest_number = serializers.CharField(
        required=False,
        validators=[validators.PhoneNumberMobileValidator()],
        error_messages={
            "invalid": "The dest number field must be a valid phone number.",
        },
    )
    call_duration = serializers.IntegerField(
        required=False,
        error_messages={
            "invalid": "The call duration field must be a positive integer.",
        },
    )
    call_successful = serializers.BooleanField(
        required=False,
        error_messages={
            "invalid": "The call successful field must be a boolean.",
        },
    )
