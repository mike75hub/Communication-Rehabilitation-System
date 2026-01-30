from rest_framework import serializers
from django.contrib.auth import get_user_model
from clients.models import Client, Address, Offense
from cases.models import Case, RehabilitationPlan, PlanItem
from appointments.models import Appointment
from comms.models import Message, Notification
from courts.models import CourtCase, Hearing
from judges.models import Judge

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'phone', 'department',
            'badge_number', 'is_active_officer'
        ]
        read_only_fields = ['id', 'username']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model"""
    class Meta:
        model = Address
        fields = ['id', 'address_type', 'street', 'city', 'state', 'zip_code', 'is_primary']


class OffenseSerializer(serializers.ModelSerializer):
    """Serializer for Offense model"""
    class Meta:
        model = Offense
        fields = ['id', 'offense_type', 'description', 'date_committed', 'sentence', 'court']


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model"""
    full_name = serializers.SerializerMethodField()
    addresses = AddressSerializer(many=True, read_only=True)
    offenses = OffenseSerializer(many=True, read_only=True)
    assigned_officer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'case_number', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'assigned_officer', 'assigned_officer_name',
            'status', 'start_date', 'end_date', 'risk_level', 'notes',
            'addresses', 'offenses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_assigned_officer_name(self, obj):
        return obj.assigned_officer.get_full_name() if obj.assigned_officer else None


class CaseSerializer(serializers.ModelSerializer):
    """Serializer for Case model"""
    client_name = serializers.SerializerMethodField()
    officer_name = serializers.SerializerMethodField()
    judge_name = serializers.SerializerMethodField()
    days_until_court = serializers.SerializerMethodField()
    
    class Meta:
        model = Case
        fields = [
            'id', 'client', 'client_name', 'officer', 'officer_name',
            'presiding_judge', 'judge_name', 'status', 'court_type',
            'case_number', 'opening_date', 'closing_date', 'sentencing_date',
            'next_court_date', 'days_until_court', 'objectives',
            'special_conditions', 'court_notes', 'is_high_profile'
        ]
    
    def get_client_name(self, obj):
        return obj.client.full_name if obj.client else None
    
    def get_officer_name(self, obj):
        return obj.officer.get_full_name() if obj.officer else None
    
    def get_judge_name(self, obj):
        return obj.presiding_judge.get_full_name() if obj.presiding_judge else None
    
    def get_days_until_court(self, obj):
        return obj.days_until_court


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    client_name = serializers.SerializerMethodField()
    officer_name = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'officer', 'officer_name',
            'appointment_type', 'status', 'scheduled_date', 'formatted_date',
            'duration_minutes', 'location', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_client_name(self, obj):
        return obj.client.full_name if obj.client else None
    
    def get_officer_name(self, obj):
        return obj.officer.get_full_name() if obj.officer else None
    
    def get_formatted_date(self, obj):
        return obj.scheduled_date.strftime('%Y-%m-%d %H:%M') if obj.scheduled_date else None


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'recipient', 'recipient_name',
            'subject', 'body', 'sent_at', 'read_at', 'is_urgent'
        ]
        read_only_fields = ['sender', 'sent_at']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if obj.sender else None
    
    def get_recipient_name(self, obj):
        return obj.recipient.get_full_name() if obj.recipient else None


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'created_at', 'is_read', 'related_object_id', 'related_content_type'
        ]
        read_only_fields = ['created_at']


# Additional serializers for court system
class JudgeSerializer(serializers.ModelSerializer):
    """Serializer for Judge model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Judge
        fields = [
            'id', 'user', 'judge_id', 'court', 'specialization',
            'appointment_date', 'full_name', 'phone', 'office_location',
            'is_active'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class CourtCaseSerializer(serializers.ModelSerializer):
    """Serializer for CourtCase model"""
    class Meta:
        model = CourtCase
        fields = '__all__'


class HearingSerializer(serializers.ModelSerializer):
    """Serializer for Hearing model"""
    class Meta:
        model = Hearing
        fields = '__all__'