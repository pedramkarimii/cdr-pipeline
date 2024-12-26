from django.core import validators
from django.utils.translation import gettext_lazy as _


class CustomRegexValidator(validators.RegexValidator):
    """
    Custom RegexValidator with enhanced error messages
    """

    def __init__(self, regex, message):
        super().__init__(regex, message=message)


class CallDuration(validators.BaseValidator):
    """
    Custom validator to check that the call duration is a positive number.
    Raises ValidationError if the value is less than or equal to 0.
    """

    def compare(self, value, limit_value):
        return value <= 0

    def clean(self, value):
        return value

    def __init__(self, limit_value=None):
        super().__init__(limit_value)
        self.message = _('Call duration must be greater than 0.')


class PhoneNumberMobileValidator(CustomRegexValidator):
    """
    Validator for phone number field
    """

    def __init__(self):
        super().__init__(
            r"09(1[0-9]|3[0-9]|2[0-9]|0[1-9]|9[0-9])[0-9]{7}$",
            _('Please enter a valid phone number in the format 09121234567.')
        )
