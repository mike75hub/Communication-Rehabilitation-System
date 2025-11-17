from django.contrib import admin
from .models import Judge, CourtAssignment, JudicialLeave

@admin.register(Judge)
class JudgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'judge_id', 'court', 'specialization', 'appointment_date', 'is_active']
    list_filter = ['specialization', 'is_active', 'court']
    search_fields = ['user__first_name', 'user__last_name', 'judge_id']
    date_hierarchy = 'appointment_date'

@admin.register(CourtAssignment)
class CourtAssignmentAdmin(admin.ModelAdmin):
    list_display = ['judge', 'court', 'assignment_date', 'end_date', 'is_primary', 'assignment_type']
    list_filter = ['is_primary', 'assignment_type', 'court']
    search_fields = ['judge__user__first_name', 'judge__user__last_name']

@admin.register(JudicialLeave)
class JudicialLeaveAdmin(admin.ModelAdmin):
    list_display = ['judge', 'start_date', 'end_date', 'leave_type', 'is_approved']
    list_filter = ['leave_type', 'is_approved']
    search_fields = ['judge__user__first_name', 'judge__user__last_name']
    date_hierarchy = 'start_date'