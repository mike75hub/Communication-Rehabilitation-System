from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

# Import models from your modules
from clients.models import Client
from cases.models import Case, RehabilitationPlan, PlanItem
from appointments.models import Appointment
from comms.models import Message, Notification
from courts.models import CourtCase, Hearing
from judges.models import Judge
from reporting.utils import generate_client_pdf_report

# Serializers (we'll create these next)
from .serializers import (
    UserSerializer, ClientSerializer, CaseSerializer,
    AppointmentSerializer, MessageSerializer, NotificationSerializer,
    CourtCaseSerializer, HearingSerializer, JudgeSerializer
)

User = get_user_model()


class CustomAuthToken(ObtainAuthToken):
    """Enhanced token authentication with user data"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username,
            'user_type': user.user_type,
            'full_name': user.get_full_name(),
        })


class CurrentUserView(APIView):
    """Get current authenticated user details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    """CRUD API for clients with role-based permissions"""
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_officer():
            return Client.objects.filter(assigned_officer=user)
        elif user.is_judge():
            # Judges see clients from their cases
            return Client.objects.filter(cases__presiding_judge=user).distinct()
        else:
            # Admins see all
            return Client.objects.all()
    
    @action(detail=True, methods=['get'])
    def ai_analysis(self, request, pk=None):
        """Get AI analysis for a specific client"""
        from clients.views import generate_ai_analysis
        
        client = self.get_object()
        appointments = client.appointment_set.all()
        
        # Get cases using the correct related name
        try:
            cases = client.cases.all()
        except AttributeError:
            from cases.models import Case
            cases = Case.objects.filter(client=client)
        
        offenses = client.offenses.all()
        
        analysis = generate_ai_analysis(client, appointments, cases, offenses)
        return Response(analysis)


class AppointmentViewSet(viewsets.ModelViewSet):
    """CRUD API for appointments"""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Date filtering
        date_filter = self.request.query_params.get('date', None)
        status_filter = self.request.query_params.get('status', None)
        
        queryset = Appointment.objects.all()
        
        if user.is_officer():
            queryset = queryset.filter(officer=user)
        
        if date_filter:
            queryset = queryset.filter(scheduled_date__date=date_filter)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('scheduled_date')
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        today = timezone.now().date()
        appointments = self.get_queryset().filter(scheduled_date__date=today)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments (next 7 days)"""
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        appointments = self.get_queryset().filter(
            scheduled_date__date__range=[today, next_week]
        )
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)


class CaseViewSet(viewsets.ModelViewSet):
    """CRUD API for cases"""
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_officer():
            return Case.objects.filter(officer=user)
        elif user.is_judge():
            return Case.objects.filter(presiding_judge=user)
        else:
            return Case.objects.all()
    
    @action(detail=True, methods=['get'])
    def rehabilitation_plans(self, request, pk=None):
        """Get rehabilitation plans for a case"""
        case = self.get_object()
        plans = case.rehabilitation_plans.all()
        # You would create a RehabilitationPlanSerializer for this
        return Response({
            'case_id': case.id,
            'plans_count': plans.count(),
            'plans': [{'id': p.id, 'title': p.title} for p in plans]
        })


class MessageViewSet(viewsets.ModelViewSet):
    """CRUD API for messages"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by('-sent_at')
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread messages count"""
        count = Message.objects.filter(
            recipient=request.user,
            read_at__isnull=True
        ).count()
        return Response({'unread_count': count})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API for notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})


class DashboardView(APIView):
    """API endpoint for dashboard data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        response_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'full_name': user.get_full_name(),
            },
            'stats': {}
        }
        
        if user.is_officer():
            # Officer dashboard stats
            total_clients = Client.objects.filter(assigned_officer=user).count()
            active_cases = Case.objects.filter(officer=user, status='open').count()
            todays_appointments = Appointment.objects.filter(
                scheduled_date__date=timezone.now().date(),
                officer=user
            ).count()
            
            response_data['stats'] = {
                'total_clients': total_clients,
                'active_cases': active_cases,
                'todays_appointments': todays_appointments,
            }
            
        elif user.is_judge():
            # Judge dashboard stats
            try:
                judge_profile = Judge.objects.get(user=user)
                active_court_cases = CourtCase.objects.filter(
                    judge=judge_profile, 
                    status='ACTIVE'
                ).count()
                upcoming_hearings = Hearing.objects.filter(
                    judge=judge_profile,
                    hearing_date__gte=timezone.now(),
                    is_completed=False
                ).count()
                
                response_data['stats'] = {
                    'active_court_cases': active_court_cases,
                    'upcoming_hearings': upcoming_hearings,
                }
            except Judge.DoesNotExist:
                pass
        
        return Response(response_data)


class ReportAPIView(APIView):
    """API for generating reports"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        report_type = request.query_params.get('type', 'clients')
        format_type = request.query_params.get('format', 'json')
        
        if report_type == 'clients':
            if format_type == 'pdf':
                # Generate PDF report
                from reporting.utils import generate_client_pdf_report
                return generate_client_pdf_report()
            else:
                # JSON client report
                clients = Client.objects.all()
                serializer = ClientSerializer(clients, many=True)
                return Response({
                    'report_type': 'clients',
                    'count': clients.count(),
                    'data': serializer.data
                })
        
        return Response({'error': 'Invalid report type'}, status=400)


class SyncView(APIView):
    """API for data synchronization (offline support)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Sync data from mobile/client"""
        sync_data = request.data
        user = request.user
        
        # Handle appointment sync
        if 'appointments' in sync_data:
            for appt_data in sync_data['appointments']:
                # Update or create appointments
                pass
        
        # Handle client updates
        if 'clients' in sync_data:
            for client_data in sync_data['clients']:
                # Update client information
                pass
        
        return Response({'status': 'sync completed', 'received_items': len(sync_data)})
    
class OfficerListView(APIView):
    """Get list of active probation officers"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        officers = User.objects.filter(
            user_type='officer', 
            is_active_officer=True
        ).order_by('first_name', 'last_name')
        
        serializer = UserSerializer(officers, many=True)
        return Response(serializer.data)


class JudgeListView(APIView):
    """Get list of judges"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        judges = Judge.objects.filter(is_active=True)
        serializer = JudgeSerializer(judges, many=True)
        return Response(serializer.data)


