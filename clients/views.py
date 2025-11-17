from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Client, Address, Offense
from .forms import ClientForm, AddressForm, OffenseForm

@login_required
def client_list(request):
    query = request.GET.get('q')
    
    # Show different client lists based on user role
    if request.user.user_type == 'officer':
        # Officers see only their assigned clients
        clients = Client.objects.filter(assigned_officer=request.user)
    else:
        # Admins and staff see all clients
        clients = Client.objects.all()
    
    if query:
        clients = clients.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(case_number__icontains=query)
        )
    
    context = {
        'clients': clients,
        'search_query': query
    }
    return render(request, 'clients/client_list.html', context)

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    # Check if user has permission to view this client
    if request.user.user_type == 'officer' and client.assigned_officer != request.user:
        messages.error(request, "You don't have permission to view this client.")
        return redirect('client_list')
    
    addresses = client.addresses.all()
    offenses = client.offenses.all()
    
    # Get basic analysis for the detail page
    basic_analysis = generate_basic_analysis(client)
    
    context = {
        'client': client,
        'addresses': addresses,
        'offenses': offenses,
        'basic_analysis': basic_analysis
    }
    return render(request, 'clients/client_detail.html', context)

@login_required
def client_create(request):
    # Check if user can add clients
    if not request.user.can_add_clients():
        messages.error(request, "You don't have permission to add clients.")
        return redirect('client_list')
    
    if request.method == 'POST':
        form = ClientForm(request.POST, request=request)
        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = request.user  # Set the creator
            client.save()
            messages.success(request, f'Client {client.full_name} created successfully!')
            return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm(request=request)
        # Set initial assigned officer to current user if they are an officer
        if request.user.user_type == 'officer':
            form.fields['assigned_officer'].initial = request.user
    
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Add Client'})

@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    # Check if user has permission to edit this client
    if request.user.user_type == 'officer' and client.assigned_officer != request.user:
        messages.error(request, "You don't have permission to edit this client.")
        return redirect('client_list')
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client {client.full_name} updated successfully!')
            return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client, request=request)
    
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Edit Client'})

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    # Check if user has permission to delete this client
    if not request.user.user_type == 'admin':
        messages.error(request, "Only administrators can delete clients.")
        return redirect('client_list')
    
    if request.method == 'POST':
        client_name = client.full_name
        client.delete()
        messages.success(request, f'Client {client_name} deleted successfully!')
        return redirect('client_list')
    
    return render(request, 'clients/client_confirm_delete.html', {'client': client})

@login_required
def ai_analyzer(request, pk):
    """Comprehensive AI analysis for a client"""
    client = get_object_or_404(Client, pk=pk)
    
    # Check if user has permission to view this client's analysis
    if hasattr(request.user, 'user_type') and request.user.user_type == 'officer' and client.assigned_officer != request.user:
        messages.error(request, "You don't have permission to view this client's analysis.")
        return redirect('client_list')
    # Get client data for analysis
    appointments = client.appointment_set.all()
        # Attempt to get cases using related_name; fallback to default if necessary 
    try:
        cases = client.cases.all()  # This uses the related_name from your Case model
    except AttributeError:
        try:
            cases = client.case_set.all()  # Fall back to default
        except AttributeError:
            # If neither works, use direct filter
            from cases.models import Case
            cases = Case.objects.filter(client=client)
    
    
    
    offenses = client.offenses.all()
    # AI Analysis Logic
    analysis_results = generate_ai_analysis(client, appointments, cases, offenses)
    
    context = {
        'client': client,
        'appointments': appointments,
        'cases': cases,
        'offenses': offenses,
        'analysis': analysis_results,
    }
    
    return render(request, 'clients/ai_analyzer.html', context)

def generate_basic_analysis(client):
    """Generate basic analysis for client detail page"""
    appointments = client.appointment_set.all()
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='completed').count()
    
    completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
    
    # Simple risk indicator
    if completion_rate < 70:
        risk_indicator = 'warning'
    elif completion_rate < 50:
        risk_indicator = 'danger'
    else:
        risk_indicator = 'success'
    
    return {
        'completion_rate': completion_rate,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'risk_indicator': risk_indicator,
    }

def generate_ai_analysis(client, appointments, cases, offenses):
    """Generate AI-based analysis for a client"""
    
    # Calculate basic metrics
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='completed').count()
    missed_appointments = appointments.filter(status='no_show').count()
    
    completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
    
    # Risk factors analysis
    risk_factors = []
    recommendations = []
    
    # Analyze appointment compliance
    if completion_rate < 70:
        risk_factors.append({
            'factor': 'Low appointment compliance',
            'severity': 'high',
            'description': f'Only {completion_rate:.1f}% of appointments completed'
        })
        recommendations.append('Increase monitoring frequency')
        recommendations.append('Implement stricter check-in requirements')
    
    # Analyze recent behavior
    recent_appointments = appointments.filter(
        scheduled_date__gte=timezone.now() - timedelta(days=30)
    )
    recent_missed = recent_appointments.filter(status='no_show').count()
    
    if recent_missed > 2:
        risk_factors.append({
            'factor': 'Multiple recent missed appointments',
            'severity': 'high',
            'description': f'{recent_missed} missed appointments in last 30 days'
        })
        recommendations.append('Schedule immediate intervention')
        recommendations.append('Consider home visit assessment')
    
    # Analyze offense history
    if offenses.count() > 3:
        risk_factors.append({
            'factor': 'Extensive offense history',
            'severity': 'medium',
            'description': f'{offenses.count()} prior offenses recorded'
        })
        recommendations.append('Focus on rehabilitation program adherence')
    
    # Analyze case progress
    active_cases = cases.filter(status='open')
    if active_cases.count() > 1:
        risk_factors.append({
            'factor': 'Multiple active cases',
            'severity': 'medium',
            'description': f'{active_cases.count()} concurrent active cases'
        })
    
    # Generate overall risk score (0-100, higher = more risk)
    base_risk = client.risk_level
    base_scores = {'low': 25, 'medium': 50, 'high': 75}
    risk_score = base_scores.get(base_risk, 50)
    
    # Adjust based on factors
    for factor in risk_factors:
        if factor['severity'] == 'high':
            risk_score += 10
        elif factor['severity'] == 'medium':
            risk_score += 5
    
    risk_score = min(100, max(0, risk_score))
    
    # Determine risk category
    if risk_score >= 75:
        risk_category = 'High Risk'
        alert_level = 'danger'
    elif risk_score >= 50:
        risk_category = 'Medium Risk'
        alert_level = 'warning'
    else:
        risk_category = 'Low Risk'
        alert_level = 'success'
    
    return {
        'risk_score': risk_score,
        'risk_category': risk_category,
        'alert_level': alert_level,
        'completion_rate': completion_rate,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'missed_appointments': missed_appointments,
        'risk_factors': risk_factors,
        'recommendations': recommendations,
        'analysis_date': timezone.now(),
    }