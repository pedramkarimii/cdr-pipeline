from django.db import models
from django.utils import timezone
from apps.core import validators
from django.utils.translation import gettext_lazy as _


class Cdr(models.Model):
    """Model to represent a Call Detail Record (CDR)"""

    src_number = models.CharField(
        max_length=11, unique=True,
        validators=[validators.PhoneNumberMobileValidator()], verbose_name=_('Phone Number Src')
    )

    dest_number = models.CharField(
        max_length=11, unique=True,
        validators=[validators.PhoneNumberMobileValidator()], verbose_name=_('Phone Number Dest')
    )

    call_duration = models.PositiveIntegerField(
        validators=[validators.CallDuration()],
        null=True,
        blank=True,
        help_text="Duration of the call in seconds"
    )

    start_time = models.DateTimeField(default=timezone.now, editable=False)
    end_time = models.DateTimeField(default=timezone.now, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
    call_successful = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.src_number} -> {self.dest_number} | {self.call_duration}s | {"Success" if self.call_successful else "Failed"}'

    class Meta:
        indexes = [
            models.Index(fields=['src_number', 'dest_number', 'timestamp']),
        ]
        verbose_name = "Call Detail Record"
        verbose_name_plural = "Call Detail Records"
        constraints = [
            models.UniqueConstraint(fields=['src_number', 'dest_number'], name='unique_src_dest_numbers')
        ]
