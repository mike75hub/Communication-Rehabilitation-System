from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
from clients.models import Client
from cases.models import Case
from appointments.models import Appointment
from users.models import User
import csv

@login_required
def report_list(request):
    return render(request, 'reporting/report_list.html')

@login_required
def client_report(request):
    # Basic client statistics
    clients = Client.objects.all().select_related('assigned_officer')
    total_clients = clients.count()
    active_clients = clients.filter(status='active').count()
    completed_clients = clients.filter(status='completed').count()
    violated_clients = clients.filter(status='violated').count()
    
    # Risk level breakdown
    risk_levels = Client.objects.values('risk_level').annotate(
        count=Count('risk_level')
    )
    total_risk = sum(level['count'] for level in risk_levels)
    for level in risk_levels:
        level['percentage'] = (level['count'] / total_risk * 100) if total_risk > 0 else 0
    
    # Status breakdown
    status_counts = Client.objects.values('status').annotate(
        count=Count('status')
    )
    total_status = sum(status['count'] for status in status_counts)
    for status in status_counts:
        status['percentage'] = (status['count'] / total_status * 100) if total_status > 0 else 0
    
    context = {
        'clients': clients,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'completed_clients': completed_clients,
        'violated_clients': violated_clients,
        'risk_levels': risk_levels,
        'status_counts': status_counts,
    }
    
    if request.GET.get('format') == 'csv':
        return generate_client_csv_report()
    
    return render(request, 'reporting/client_report.html', context)

@login_required
def appointment_report(request):
    # Last 30 days appointments
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    appointments = Appointment.objects.filter(
        scheduled_date__gte=thirty_days_ago
    ).order_by('-scheduled_date')
    
    # Appointment type breakdown
    type_breakdown = appointments.values('appointment_type').annotate(
        count=Count('appointment_type')
    )
    total_type = sum(item['count'] for item in type_breakdown)
    for item in type_breakdown:
        item['percentage'] = (item['count'] / total_type * 100) if total_type > 0 else 0
    
    # Status breakdown
    status_breakdown = appointments.values('status').annotate(
        count=Count('status')
    )
    total_status = sum(item['count'] for item in status_breakdown)
    for item in status_breakdown:
        item['percentage'] = (item['count'] / total_status * 100) if total_status > 0 else 0
    
    # Counts for summary
    completed_count = appointments.filter(status='completed').count()
    scheduled_count = appointments.filter(status='scheduled').count()
    missed_count = appointments.filter(status='no_show').count()
    
    context = {
        'appointments': appointments,
        'type_breakdown': type_breakdown,
        'status_breakdown': status_breakdown,
        'period': 'Last 30 Days',
        'completed_count': completed_count,
        'scheduled_count': scheduled_count,
        'missed_count': missed_count,
    }
    
    return render(request, 'reporting/appointment_report.html', context)

@login_required
def officer_report(request):
    # Officer workload statistics
    officers = User.objects.filter(user_type='officer').annotate(
        client_count=Count('client'),
        case_count=Count('officer_cases'),
        appointment_count=Count('appointment')
    )
    
    # Overall statistics
    total_clients = Client.objects.count()
    active_cases = Case.objects.filter(status='open').count()
    total_appointments = Appointment.objects.count()
    
    context = {
        'officers': officers,
        'total_clients': total_clients,
        'active_cases': active_cases,
        'total_appointments': total_appointments,
    }
    
    return render(request, 'reporting/officer_report.html', context)

def generate_client_csv_report():
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="client_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Case Number', 'Name', 'Status', 'Risk Level', 'Assigned Officer', 'Start Date'])
    
    clients = Client.objects.all().select_related('assigned_officer')
    for client in clients:
        writer.writerow([
            client.case_number,
            client.full_name,
            client.get_status_display(),
            client.get_risk_level_display(),
            client.assigned_officer.get_full_name(),
            client.start_date
        ])
    
    return response

@login_required
def client_report_pdf(request):
    from .utils import generate_client_pdf_report
    return generate_client_pdf_report()