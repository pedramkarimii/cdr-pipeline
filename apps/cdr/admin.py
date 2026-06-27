from django.contrib import admin

from apps.cdr.models import Cdr


@admin.register(Cdr)
class CdrAdmin(admin.ModelAdmin):
    list_display = (
        "src_number",
        "dest_number",
        "call_duration",
        "start_time",
        "end_time",
        "call_successful",
        "timestamp",
    )
    list_filter = ("call_successful", "start_time", "end_time")
    search_fields = ("src_number", "dest_number")
    list_editable = ("call_successful",)
    ordering = ("-timestamp",)
    date_hierarchy = "timestamp"
    list_per_page = 20
    readonly_fields = ("start_time", "end_time", "timestamp")
