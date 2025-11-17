from django.contrib import admin
from .models import Court, CourtCase, Hearing, CourtOrder

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['name', 'court_type', 'phone', 'clerk_name', 'is_active']
    list_filter = ['court_type', 'is_active']
    search_fields = ['name', 'clerk_name']
    list_editable = ['is_active']

@admin.register(CourtCase)
class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'case', 'court', 'judge', 'filing_date', 'status']
    list_filter = ['status', 'court', 'judge']
    search_fields = ['case_number', 'case__client__first_name', 'case__client__last_name']
    date_hierarchy = 'filing_date'

@admin.register(Hearing)
class HearingAdmin(admin.ModelAdmin):
    list_display = ['court_case', 'hearing_type', 'hearing_date', 'judge', 'is_completed']
    list_filter = ['hearing_type', 'is_completed', 'judge']
    search_fields = ['court_case__case_number']
    date_hierarchy = 'hearing_date'

@admin.register(CourtOrder)
class CourtOrderAdmin(admin.ModelAdmin):
    list_display = ['court_case', 'order_type', 'order_date', 'judge', 'is_active']
    list_filter = ['order_type', 'is_active', 'judge']
    search_fields = ['court_case__case_number']
    date_hierarchy = 'order_date'