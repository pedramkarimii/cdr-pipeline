from django.contrib import admin
from .models import Cdr


@admin.register(Cdr)
class CdrAdmin(admin.ModelAdmin):
    list_display = (
        'src_number', 'dest_number', 'call_duration', 'start_time', 'end_time', 'call_successful', 'timestamp')
    list_filter = ('call_successful', 'start_time', 'end_time')
    search_fields = ('src_number', 'dest_number')
    list_editable = ('call_successful',)
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    list_per_page = 20

    fieldsets = (
        (None, {'fields': (
        'src_number', 'dest_number', 'call_duration', 'start_time', 'end_time', 'timestamp', 'call_successful')}),
    )

    add_fieldsets = (
        (None, {'fields': (
        'src_number', 'dest_number', 'call_duration', 'start_time', 'end_time', 'timestamp', 'call_successful')}),
    )

    readonly_fields = ('start_time', 'end_time', 'timestamp')

    def save_model(self, request, obj, form, change):
        if not change:  # Only validate on new record creation
            if Cdr.objects.filter(src_number=obj.src_number, dest_number=obj.dest_number).exists():
                raise ValueError('The combination of src_number and dest_number must be unique.')
        super().save_model(request, obj, form, change)
