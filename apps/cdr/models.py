from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core import validators


class Cdr(models.Model):
    src_number = models.CharField(
        max_length=11,
        validators=[validators.PhoneNumberMobileValidator()],
        verbose_name=_("Source phone number"),
        db_index=True,
    )
    dest_number = models.CharField(
        max_length=11,
        validators=[validators.PhoneNumberMobileValidator()],
        verbose_name=_("Destination phone number"),
        db_index=True,
    )
    call_duration = models.PositiveIntegerField(
        validators=[validators.CallDuration()],
        null=True,
        blank=True,
        help_text="Duration of the call in seconds",
    )
    start_time = models.DateTimeField(default=timezone.now, editable=False)
    end_time = models.DateTimeField(default=timezone.now, editable=False)
    timestamp = models.DateTimeField(
        default=timezone.now,
        editable=False,
        db_index=True,
    )
    call_successful = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["src_number", "dest_number", "timestamp"]),
        ]
        verbose_name = "Call Detail Record"
        verbose_name_plural = "Call Detail Records"

    def __str__(self):
        outcome = "Success" if self.call_successful else "Failed"
        return (
            f"{self.src_number} -> {self.dest_number} | "
            f"{self.call_duration}s | {outcome}"
        )
