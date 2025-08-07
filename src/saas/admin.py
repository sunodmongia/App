from django.contrib import admin
from saas.models import *


@admin.register(TrialSignup)
class TrialSignupAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'company', 'created_at')
    list_filter = ('company_size', 'industry', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'created_at')

@admin.register(DemoSchedule)
class DemoScheduleAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'company', 'time_slot','preferred_date', 'created_at')
    list_filter =  ('company_size', 'preferred_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'company')
