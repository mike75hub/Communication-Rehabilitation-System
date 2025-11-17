from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import timedelta, datetime
import json

from .models import Court, CourtCase, Hearing, CourtOrder
from .forms import CourtForm, CourtCaseForm, HearingForm, CourtOrderForm
from judges.models import Judge
from cases.models import Case

@login_required
def court_dashboard(request):
    """Court system dashboard"""
    # Court statistics
    total_courts = Court.objects.filter(is_active=True).count()
    total_judges = Judge.objects.filter(is_active=True).count()
    total_court_cases = CourtCase.objects.count()
    upcoming_hearings = Hearing.objects.filter(
        hearing_date__gte=timezone.now(),
        is_completed=False
    ).count()
    
    # Recent activity
    recent_hearings = Hearing.objects.filter(
        hearing_date__gte=timezone.now() - timedelta(days=7)
    ).order_by('-hearing_date')[:5]
    
    recent_orders = CourtOrder.objects.all().order_by('-order_date')[:5]
    
    # Today's hearings
    todays_hearings = Hearing.objects.filter(
        hearing_date__date=timezone.now().date()
    ).order_by('hearing_date')
    
    context = {
        'total_courts': total_courts,
        'total_judges': total_judges,
        'total_court_cases': total_court_cases,
        'upcoming_hearings': upcoming_hearings,
        'recent_hearings': recent_hearings,
        'recent_orders': recent_orders,
        'todays_hearings': todays_hearings,
    }
    return render(request, 'courts/court_dashboard.html', context)

@login_required
def court_list(request):
    """List all courts"""
    courts = Court.objects.filter(is_active=True)
    
    # Filter options
    court_type = request.GET.get('court_type')
    search = request.GET.get('search')
    
    if court_type:
        courts = courts.filter(court_type=court_type)
    if search:
        courts = courts.filter(
            Q(name__icontains=search) |
            Q(clerk_name__icontains=search) |
            Q(address__icontains=search)
        )
    
    context = {
        'courts': courts,
        'court_type_filter': court_type,
        'search_query': search,
    }
    return render(request, 'courts/court_list.html', context)

@login_required
def court_create(request):
    """Create a new court"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff only.")
        return redirect('courts:court_list')
    
    if request.method == 'POST':
        form = CourtForm(request.POST)
        if form.is_valid():
            court = form.save()
            messages.success(request, f'Court "{court.name}" created successfully!')
            return redirect('courts:court_detail', pk=court.pk)
    else:
        form = CourtForm()
    
    context = {
        'form': form,
        'title': 'Create New Court',
        'submit_text': 'Create Court'
    }
    return render(request, 'courts/court_form.html', context)

@login_required
def court_detail(request, pk):
    """Detailed view of a court"""
    court = get_object_or_404(Court, pk=pk)
    
    # Get assigned judges
    assigned_judges = Judge.objects.filter(court=court, is_active=True)
    
    # Get court cases
    court_cases = CourtCase.objects.filter(court=court)
    
    # Get upcoming hearings
    upcoming_hearings = Hearing.objects.filter(
        court_case__court=court,
        hearing_date__gte=timezone.now()
    ).order_by('hearing_date')[:10]
    
    # Statistics
    active_cases = court_cases.filter(status='ACTIVE').count()
    pending_cases = court_cases.filter(status='PENDING').count()
    closed_cases = court_cases.filter(status='CLOSED').count()
    
    context = {
        'court': court,
        'assigned_judges': assigned_judges,
        'court_cases': court_cases,
        'upcoming_hearings': upcoming_hearings,
        'active_cases': active_cases,
        'pending_cases': pending_cases,
        'closed_cases': closed_cases,
    }
    return render(request, 'courts/court_detail.html', context)

@login_required
def court_edit(request, pk):
    """Edit court information"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff only.")
        return redirect('courts:court_detail', pk=pk)
    
    court = get_object_or_404(Court, pk=pk)
    
    if request.method == 'POST':
        form = CourtForm(request.POST, instance=court)
        if form.is_valid():
            court = form.save()
            messages.success(request, f'Court "{court.name}" updated successfully!')
            return redirect('courts:court_detail', pk=court.pk)
    else:
        form = CourtForm(instance=court)
    
    context = {
        'form': form,
        'court': court,
        'title': f'Edit Court: {court.name}',
        'submit_text': 'Update Court'
    }
    return render(request, 'courts/court_form.html', context)

@login_required
def court_delete(request, pk):
    """Delete a court (soft delete)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff only.")
        return redirect('courts:court_list')
    
    court = get_object_or_404(Court, pk=pk)
    
    if request.method == 'POST':
        court.is_active = False
        court.save()
        messages.success(request, f'Court "{court.name}" deleted successfully!')
        return redirect('courts:court_list')
    
    return render(request, 'courts/court_confirm_delete.html', {'court': court})

@login_required
def court_case_list(request):
    """List all court cases"""
    court_cases = CourtCase.objects.all().order_by('-filing_date')
    
    # Filter options
    status_filter = request.GET.get('status')
    court_filter = request.GET.get('court')
    judge_filter = request.GET.get('judge')
    search = request.GET.get('search')
    
    if status_filter:
        court_cases = court_cases.filter(status=status_filter)
    if court_filter:
        court_cases = court_cases.filter(court_id=court_filter)
    if judge_filter:
        court_cases = court_cases.filter(judge_id=judge_filter)
    if search:
        court_cases = court_cases.filter(
            Q(case_number__icontains=search) |
            Q(case__client__first_name__icontains=search) |
            Q(case__client__last_name__icontains=search)
        )
    
    courts = Court.objects.filter(is_active=True)
    judges = Judge.objects.filter(is_active=True)
    
    context = {
        'court_cases': court_cases,
        'courts': courts,
        'judges': judges,
        'status_filter': status_filter,
        'court_filter': court_filter,
        'judge_filter': judge_filter,
        'search_query': search,
    }
    return render(request, 'courts/court_case_list.html', context)

@login_required
def court_case_create(request):
    """Create a new court case"""
    if request.method == 'POST':
        form = CourtCaseForm(request.POST)
        if form.is_valid():
            court_case = form.save()
            messages.success(request, f'Court case "{court_case.case_number}" created successfully!')
            return redirect('courts:court_case_detail', pk=court_case.pk)
    else:
        form = CourtCaseForm()
    
    context = {
        'form': form,
        'title': 'Create New Court Case',
        'submit_text': 'Create Case'
    }
    return render(request, 'courts/court_case_form.html', context)

@login_required
def court_case_detail(request, pk):
    """Detailed view of a court case"""
    court_case = get_object_or_404(CourtCase, pk=pk)
    hearings = Hearing.objects.filter(court_case=court_case).order_by('hearing_date')
    orders = CourtOrder.objects.filter(court_case=court_case).order_by('-order_date')
    
    context = {
        'court_case': court_case,
        'hearings': hearings,
        'orders': orders,
    }
    return render(request, 'courts/court_case_detail.html', context)

@login_required
def court_case_edit(request, pk):
    """Edit court case information"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff only.")
        return redirect('courts:court_case_detail', pk=pk)
    
    court_case = get_object_or_404(CourtCase, pk=pk)
    
    if request.method == 'POST':
        form = CourtCaseForm(request.POST, instance=court_case)
        if form.is_valid():
            court_case = form.save()
            messages.success(request, f'Court case "{court_case.case_number}" updated successfully!')
            return redirect('courts:court_case_detail', pk=court_case.pk)
    else:
        form = CourtCaseForm(instance=court_case)
    
    context = {
        'form': form,
        'court_case': court_case,
        'title': f'Edit Court Case: {court_case.case_number}',
        'submit_text': 'Update Case'
    }
    return render(request, 'courts/court_case_form.html', context)

@login_required
def hearing_list(request):
    """List all hearings"""
    hearings = Hearing.objects.all().order_by('hearing_date')
    
    # Filter options
    court_filter = request.GET.get('court')
    judge_filter = request.GET.get('judge')
    completed_filter = request.GET.get('completed')
    
    if court_filter:
        hearings = hearings.filter(court_case__court_id=court_filter)
    if judge_filter:
        hearings = hearings.filter(judge_id=judge_filter)
    if completed_filter == 'true':
        hearings = hearings.filter(is_completed=True)
    elif completed_filter == 'false':
        hearings = hearings.filter(is_completed=False)
    
    courts = Court.objects.filter(is_active=True)
    judges = Judge.objects.filter(is_active=True)
    
    context = {
        'hearings': hearings,
        'courts': courts,
        'judges': judges,
        'court_filter': court_filter,
        'judge_filter': judge_filter,
        'completed_filter': completed_filter,
    }
    return render(request, 'courts/hearing_list.html', context)

@login_required
def hearing_create(request):
    """Schedule a new hearing"""
    if request.method == 'POST':
        form = HearingForm(request.POST)
        if form.is_valid():
            hearing = form.save()
            messages.success(request, f'Hearing scheduled successfully for {hearing.hearing_date.strftime("%Y-%m-%d")}!')
            return redirect('courts:hearing_list')
    else:
        form = HearingForm()
    
    context = {
        'form': form,
        'title': 'Schedule New Hearing',
        'submit_text': 'Schedule Hearing'
    }
    return render(request, 'courts/hearing_form.html', context)

@login_required
def hearing_detail(request, pk):
    """Detailed view of a hearing"""
    hearing = get_object_or_404(Hearing, pk=pk)
    
    context = {
        'hearing': hearing,
    }
    return render(request, 'courts/hearing_detail.html', context)

@login_required
def hearing_edit(request, pk):
    """Edit hearing information"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff only.")
        return redirect('courts:hearing_detail', pk=pk)
    
    hearing = get_object_or_404(Hearing, pk=pk)
    
    if request.method == 'POST':
        form = HearingForm(request.POST, instance=hearing)
        if form.is_valid():
            hearing = form.save()
            messages.success(request, f'Hearing updated successfully!')
            return redirect('courts:hearing_detail', pk=hearing.pk)
    else:
        form = HearingForm(instance=hearing)
    
    context = {
        'form': form,
        'hearing': hearing,
        'title': f'Edit Hearing',
        'submit_text': 'Update Hearing'
    }
    return render(request, 'courts/hearing_form.html', context)

@login_required
def hearing_update_status(request, pk):
    """Update hearing status (complete/incomplete)"""
    hearing = get_object_or_404(Hearing, pk=pk)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        is_completed = data.get('is_completed')
        outcome = data.get('outcome', '')
        
        hearing.is_completed = is_completed
        hearing.outcome = outcome
        hearing.save()
        
        messages.success(request, f'Hearing status updated successfully!')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def court_order_list(request):
    """List all court orders"""
    court_orders = CourtOrder.objects.all().order_by('-order_date')
    
    # Filter options
    order_type_filter = request.GET.get('order_type')
    court_filter = request.GET.get('court')
    judge_filter = request.GET.get('judge')
    
    if order_type_filter:
        court_orders = court_orders.filter(order_type=order_type_filter)
    if court_filter:
        court_orders = court_orders.filter(court_case__court_id=court_filter)
    if judge_filter:
        court_orders = court_orders.filter(judge_id=judge_filter)
    
    courts = Court.objects.filter(is_active=True)
    judges = Judge.objects.filter(is_active=True)
    
    context = {
        'court_orders': court_orders,
        'courts': courts,
        'judges': judges,
        'order_type_filter': order_type_filter,
        'court_filter': court_filter,
        'judge_filter': judge_filter,
    }
    return render(request, 'courts/court_order_list.html', context)

@login_required
def court_order_create(request):
    """Create a new court order"""
    if request.method == 'POST':
        form = CourtOrderForm(request.POST, request.FILES)
        if form.is_valid():
            court_order = form.save()
            messages.success(request, f'Court order created successfully!')
            return redirect('courts:court_order_list')
    else:
        form = CourtOrderForm()
    
    context = {
        'form': form,
        'title': 'Create New Court Order',
        'submit_text': 'Create Order'
    }
    return render(request, 'courts/court_order_form.html', context)

@login_required
def court_order_detail(request, pk):
    """Detailed view of a court order"""
    court_order = get_object_or_404(CourtOrder, pk=pk)
    
    context = {
        'court_order': court_order,
    }
    return render(request, 'courts/court_order_detail.html', context)

@login_required
def court_order_edit(request, pk):
    """Edit court order information"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff only.")
        return redirect('courts:court_order_detail', pk=pk)
    
    court_order = get_object_or_404(CourtOrder, pk=pk)
    
    if request.method == 'POST':
        form = CourtOrderForm(request.POST, request.FILES, instance=court_order)
        if form.is_valid():
            court_order = form.save()
            messages.success(request, f'Court order updated successfully!')
            return redirect('courts:court_order_detail', pk=court_order.pk)
    else:
        form = CourtOrderForm(instance=court_order)
    
    context = {
        'form': form,
        'court_order': court_order,
        'title': f'Edit Court Order',
        'submit_text': 'Update Order'
    }
    return render(request, 'courts/court_order_form.html', context)

@login_required
def court_calendar_overview(request):
    """Court calendar overview for all courts"""
    # Get date range (next 30 days by default)
    start_date = request.GET.get('start_date', timezone.now().date().isoformat())
    end_date = request.GET.get('end_date', (timezone.now().date() + timedelta(days=30)).isoformat())
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
    
    # Get hearings in date range
    hearings = Hearing.objects.filter(
        hearing_date__date__range=[start_date, end_date]
    ).order_by('hearing_date')
    
    # Group by date for calendar view
    calendar_events = {}
    for hearing in hearings:
        date_str = hearing.hearing_date.date().isoformat()
        if date_str not in calendar_events:
            calendar_events[date_str] = []
        calendar_events[date_str].append(hearing)
    
    courts = Court.objects.filter(is_active=True)
    
    context = {
        'hearings': hearings,
        'calendar_events': calendar_events,
        'start_date': start_date,
        'end_date': end_date,
        'courts': courts,
    }
    return render(request, 'courts/court_calendar_overview.html', context)

# AJAX views for dynamic functionality
@login_required
def get_judges_for_court(request):
    """Get judges assigned to a specific court (AJAX)"""
    court_id = request.GET.get('court_id')
    if court_id:
        judges = Judge.objects.filter(court_id=court_id, is_active=True)
        judges_data = [{'id': judge.id, 'name': str(judge)} for judge in judges]
        return JsonResponse(judges_data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def get_court_cases_for_judge(request):
    """Get court cases for a specific judge (AJAX)"""
    judge_id = request.GET.get('judge_id')
    if judge_id:
        court_cases = CourtCase.objects.filter(judge_id=judge_id, status='ACTIVE')
        cases_data = [{'id': case.id, 'number': case.case_number} for case in court_cases]
        return JsonResponse(cases_data, safe=False)
    return JsonResponse([], safe=False)