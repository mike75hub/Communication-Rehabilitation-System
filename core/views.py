from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from clients.models import Client
from cases.models import Case
from appointments.models import Appointment
from comms.models import Notification, Message

@login_required
def dashboard(request):
    # Import court models here to avoid circular imports
    from courts.models import CourtCase, Hearing, CourtOrder
    from judges.models import Judge
    
    # Get statistics for dashboard based on user role
    if request.user.user_type == 'officer':
        # Officers see only their assigned clients and cases
        total_clients = Client.objects.filter(assigned_officer=request.user).count()
        active_cases = Case.objects.filter(officer=request.user, status='open').count()
        todays_appointments = Appointment.objects.filter(
            scheduled_date__date=timezone.now().date(),
            officer=request.user
        ).count()
        clients = Client.objects.filter(assigned_officer=request.user)
        
        # Court-related stats for officers
        court_cases = CourtCase.objects.filter(case__officer=request.user)
        active_court_cases = court_cases.filter(status='ACTIVE').count()
        upcoming_hearings = Hearing.objects.filter(
            court_case__case__officer=request.user,
            hearing_date__gte=timezone.now(),
            is_completed=False
        ).count()
        
    elif request.user.user_type == 'judge':
        # Judges see their presiding cases and court-related data
        total_clients = Client.objects.filter(cases__presiding_judge=request.user).distinct().count()
        active_cases = Case.objects.filter(presiding_judge=request.user, status='open').count()
        todays_appointments = 0  # Judges don't have appointments in the same way
        
        # Get judge profile
        try:
            judge_profile = Judge.objects.get(user=request.user)
            # Court-related stats for judges
            court_cases = CourtCase.objects.filter(judge=judge_profile)
            active_court_cases = court_cases.filter(status='ACTIVE').count()
            upcoming_hearings = Hearing.objects.filter(
                judge=judge_profile,
                hearing_date__gte=timezone.now(),
                is_completed=False
            ).count()
            todays_hearings = Hearing.objects.filter(
                judge=judge_profile,
                hearing_date__date=timezone.now().date()
            ).count()
            pending_orders = CourtOrder.objects.filter(
                judge=judge_profile,
                is_active=True
            ).count()
        except Judge.DoesNotExist:
            # If no judge profile exists, set defaults
            active_court_cases = 0
            upcoming_hearings = 0
            todays_hearings = 0
            pending_orders = 0
            
        clients = Client.objects.filter(cases__presiding_judge=request.user).distinct()
        
    else:
        # Admins and staff see all data
        total_clients = Client.objects.count()
        active_cases = Case.objects.filter(status='open').count()
        todays_appointments = Appointment.objects.filter(
            scheduled_date__date=timezone.now().date()
        ).count()
        clients = Client.objects.all()
        
        # Court system statistics for admin
        active_court_cases = CourtCase.objects.filter(status='ACTIVE').count()
        upcoming_hearings = Hearing.objects.filter(
            hearing_date__gte=timezone.now(),
            is_completed=False
        ).count()
        total_courts = Court.objects.filter(is_active=True).count()
        total_judges = Judge.objects.filter(is_active=True).count()
    
    today = timezone.now().date()
    
    # Get recent appointments based on role
    if request.user.user_type == 'officer':
        recent_appointments = Appointment.objects.filter(
            scheduled_date__gte=timezone.now(),
            officer=request.user
        ).order_by('scheduled_date')[:5]
        
        # Recent court hearings for officer's cases
        recent_hearings = Hearing.objects.filter(
            court_case__case__officer=request.user,
            hearing_date__gte=timezone.now()
        ).order_by('hearing_date')[:5]
        
    elif request.user.user_type == 'judge':
        # Judges see upcoming court dates instead of appointments
        recent_appointments = []
        try:
            judge_profile = Judge.objects.get(user=request.user)
            recent_hearings = Hearing.objects.filter(
                judge=judge_profile,
                hearing_date__gte=timezone.now()
            ).order_by('hearing_date')[:5]
        except Judge.DoesNotExist:
            recent_hearings = []
            
    else:
        recent_appointments = Appointment.objects.filter(
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')[:5]
        
        # Recent hearings for admin
        recent_hearings = Hearing.objects.filter(
            hearing_date__gte=timezone.now()
        ).order_by('hearing_date')[:5]
    
    # Get recent notifications
    recent_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Calculate pending tasks
    from cases.models import PlanItem
    if request.user.user_type == 'officer':
        pending_tasks = PlanItem.objects.filter(
            rehabilitation_plan__case__officer=request.user,
            is_completed=False,
            due_date__lte=timezone.now() + timezone.timedelta(days=7)
        ).count()
        
        # Judicial review tasks for officers
        judicial_review_tasks = PlanItem.objects.filter(
            rehabilitation_plan__case__officer=request.user,
            requires_judicial_review=True,
            is_completed=False
        ).count()
        
    elif request.user.user_type == 'judge':
        pending_tasks = PlanItem.objects.filter(
            rehabilitation_plan__case__presiding_judge=request.user,
            requires_judicial_review=True,
            is_completed=False
        ).count()
        judicial_review_tasks = pending_tasks  # For judges, all pending tasks are judicial reviews
        
    else:
        pending_tasks = PlanItem.objects.filter(
            is_completed=False,
            due_date__lte=timezone.now() + timezone.timedelta(days=7)
        ).count()
        judicial_review_tasks = PlanItem.objects.filter(
            requires_judicial_review=True,
            is_completed=False
        ).count()
    
    # Get unread messages count
    unread_messages = Message.objects.filter(
        recipient=request.user,
        read_at__isnull=True
    ).count()
    
    # Get high-risk clients for alert
    if request.user.user_type == 'officer':
        high_risk_clients = Client.objects.filter(
            risk_level='high', 
            status='active',
            assigned_officer=request.user
        )[:3]
    elif request.user.user_type == 'judge':
        high_risk_clients = Client.objects.filter(
            risk_level='high', 
            status='active',
            cases__presiding_judge=request.user
        ).distinct()[:3]
    else:
        high_risk_clients = Client.objects.filter(risk_level='high', status='active')[:3]
    
    # Build context based on user role
    context = {
        'total_clients': total_clients,
        'active_cases': active_cases,
        'todays_appointments': todays_appointments,
        'pending_tasks': pending_tasks,
        'recent_appointments': recent_appointments,
        'recent_notifications': recent_notifications,
        'unread_messages': unread_messages,
        'high_risk_clients': high_risk_clients,
        'user_role': request.user.get_user_type_display(),
        'judicial_review_tasks': judicial_review_tasks,
    }
    
    # Add court system statistics based on user role
    if request.user.user_type == 'officer':
        context.update({
            'active_court_cases': active_court_cases,
            'upcoming_hearings': upcoming_hearings,
            'recent_hearings': recent_hearings,
        })
    elif request.user.user_type == 'judge':
        context.update({
            'active_court_cases': active_court_cases,
            'upcoming_hearings': upcoming_hearings,
            'todays_hearings': todays_hearings,
            'pending_orders': pending_orders,
            'recent_hearings': recent_hearings,
        })
    else:  # Admin/staff
        context.update({
            'active_court_cases': active_court_cases,
            'upcoming_hearings': upcoming_hearings,
            'total_courts': total_courts,
            'total_judges': total_judges,
            'recent_hearings': recent_hearings,
        })
    
    return render(request, 'dashboard.html', context)