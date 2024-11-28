from django.contrib import admin
from .models import Locker

@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    list_display = ('locker_id', 'status', 'user_name')
    search_fields = ('locker_id', 'user_name')
    list_filter = ('status',)



admin.site.site_header = "Locker Reservation Admin"
admin.site.site_title = "Locker Admin Portal"
admin.site.index_title = "Welcome to Locker Reservation Management"