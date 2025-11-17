from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from datetime import timedelta
from cases.models import Case
from clients.models import Client
  

@login_required
def judge_dashboard(request):
    """Dashboard specifically for judges"""
    if not request.user.is_judge():
        messages.error(request, "Access denied. Judges only.")
        return redirect('dashboard')
    
    # Get judge's cases
    presiding_cases = Case.objects.filter(presiding_judge=request.user)
    total_cases = presiding_cases.count()
    open_cases = presiding_cases.filter(status='open').count()
    sentenced_cases = presiding_cases.filter(status='sentenced').count()
    
    # Upcoming court dates
    upcoming_court_dates = presiding_cases.filter(
        next_court_date__gte=timezone.now().date()
    ).order_by('next_court_date')[:5]
    
    # Cases requiring judicial review
    review_cases = presiding_cases.filter(
        rehabilitation_plans__judicial_review_required=True,
        rehabilitation_plans__plan_items__requires_judicial_review=True,
        rehabilitation_plans__plan_items__is_completed=False
    ).distinct()
    
    # High-profile cases
    high_profile_cases = presiding_cases.filter(is_high_profile=True, status='open')
    
    context = {
        'total_cases': total_cases,
        'open_cases': open_cases,
        'sentenced_cases': sentenced_cases,
        'upcoming_court_dates': upcoming_court_dates,
        'review_cases': review_cases,
        'high_profile_cases': high_profile_cases,
    }
    
    return render(request, 'judges/judge_dashboard.html', context)

@login_required
def judge_cases(request):
    """View all cases assigned to the judge"""
    if not request.user.is_judge():
        messages.error(request, "Access denied. Judges only.")
        return redirect('dashboard')
    
    cases = Case.objects.filter(presiding_judge=request.user).order_by('-opening_date')
    
    # Filter options
    status_filter = request.GET.get('status')
    court_filter = request.GET.get('court_type')
    
    if status_filter:
        cases = cases.filter(status=status_filter)
    if court_filter:
        cases = cases.filter(court_type=court_filter)
    
    context = {
        'cases': cases,
        'status_filter': status_filter,
        'court_filter': court_filter,
    }
    
    return render(request, 'judges/judge_cases.html', context)

@login_required
def judge_case_detail(request, pk):
    """Detailed view of a specific case for judges"""
    if not request.user.is_judge():
        messages.error(request, "Access denied. Judges only.")
        return redirect('dashboard')
    
    case = get_object_or_404(Case, pk=pk, presiding_judge=request.user)
    rehabilitation_plans = case.rehabilitation_plans.all()
    
    context = {
        'case': case,
        'rehabilitation_plans': rehabilitation_plans,
    }
    
    return render(request, 'judges/judge_case_detail.html', context)

@login_required
def court_calendar(request):
    """Court calendar view for judges"""
    if not request.user.is_judge():
        messages.error(request, "Access denied. Judges only.")
        return redirect('dashboard')
    
    # Get upcoming court dates for the next 30 days
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=30)
    
    court_cases = Case.objects.filter(
        presiding_judge=request.user,
        next_court_date__range=[start_date, end_date]
    ).order_by('next_court_date')
    
    # Group by date for calendar view
    calendar_events = {}
    for case in court_cases:
        if case.next_court_date:
            date_str = case.next_court_date.isoformat()
            if date_str not in calendar_events:
                calendar_events[date_str] = []
            calendar_events[date_str].append(case)
    
    context = {
        'court_cases': court_cases,
        'calendar_events': calendar_events,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'judges/court_calendar.html', context)

@login_required
def judicial_reviews(request):
    """Cases requiring judicial review"""
    if not request.user.is_judge():
        messages.error(request, "Access denied. Judges only.")
        return redirect('dashboard')
    
    review_cases = Case.objects.filter(
        presiding_judge=request.user,
        rehabilitation_plans__judicial_review_required=True,
        rehabilitation_plans__plan_items__requires_judicial_review=True,
        rehabilitation_plans__plan_items__is_completed=False
    ).distinct()
    
    context = {
        'review_cases': review_cases,
    }
    
    return render(request, 'judges/judicial_reviews.html', context)

@login_required
def update_sentencing(request):
    """Update sentencing information for a case"""
    if not request.user.is_judge():
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        case_id = request.POST.get('case_id')
        sentencing_date = request.POST.get('sentencing_date')
        case_status = request.POST.get('case_status')
        sentencing_details = request.POST.get('sentencing_details')
        special_conditions = request.POST.get('special_conditions')
        
        try:
            case = Case.objects.get(pk=case_id, presiding_judge=request.user)
            case.sentencing_date = sentencing_date
            case.status = case_status
            case.special_conditions = special_conditions
            if sentencing_details:
                case.court_notes = f"SENTENCING: {sentencing_details}\n\n{case.court_notes}"
            case.save()
            
            return JsonResponse({'success': True})
        except Case.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Case not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def complete_review(request):
    """Complete a judicial review"""
    if not request.user.is_judge():
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        case_id = data.get('case_id')
        
        try:
            case = Case.objects.get(pk=case_id, presiding_judge=request.user)
            # Update rehabilitation plans to mark review as completed
            for plan in case.rehabilitation_plans.filter(judicial_review_required=True):
                plan.judicial_review_required = False
                plan.save()
                
                for item in plan.plan_items.filter(requires_judicial_review=True):
                    item.requires_judicial_review = False
                    item.save()
            
            return JsonResponse({'success': True})
        except Case.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Case not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def request_info(request):
    """Request additional information from probation officer"""
    if not request.user.is_judge():
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        case_id = data.get('case_id')
        info_request = data.get('request')
        
        try:
            case = Case.objects.get(pk=case_id, presiding_judge=request.user)
            # Here you would typically create a notification or message to the officer
            # For now, we'll just update court notes
            case.court_notes = f"INFO REQUESTED: {info_request}\n\n{case.court_notes}"
            case.save()
            
            return JsonResponse({'success': True})
        except Case.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Case not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def reschedule_hearing(request):
    """Reschedule a court hearing"""
    if not request.user.is_judge():
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        case_id = data.get('case_id')
        new_date = data.get('new_date')
        
        try:
            case = Case.objects.get(pk=case_id, presiding_judge=request.user)
            case.next_court_date = new_date
            case.save()
            
            return JsonResponse({'success': True})
        except Case.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Case not found'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date format'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})