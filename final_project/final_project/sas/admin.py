from django.contrib import admin
from .models import table_classes
from django.contrib.auth import get_user_model

User = get_user_model()
# Register your models here.
@admin.register(table_classes)
class table_classes_admin(admin.ModelAdmin):
    list_display = ("class_code", "class_name", "class_day", "class_start_time", "class_end_time", "display_attendees")
    search_fields = ("class_code", "class_name", "class_day", "class_start_time", "class_end_time")
    list_filter = ("class_day", "class_start_time", "class_end_time")

    def display_attendees(self, obj):
        attendees = obj.attendees.all()
        return ', '.join([str(attendee) for attendee in attendees])

    display_attendees.short_description = "Attendees"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "attendees":
            kwargs["queryset"] = User.objects.filter(role="student")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

