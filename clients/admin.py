from django.contrib import admin
from .models import Client, Address, Offense

class AddressInline(admin.TabularInline):
    model = Address
    extra = 1

class OffenseInline(admin.TabularInline):
    model = Offense
    extra = 1

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'first_name', 'last_name', 'assigned_officer', 'status', 'risk_level')
    list_filter = ('status', 'risk_level', 'assigned_officer')
    search_fields = ('case_number', 'first_name', 'last_name')
    inlines = [AddressInline, OffenseInline]

admin.site.register(Address)
admin.site.register(Offense)