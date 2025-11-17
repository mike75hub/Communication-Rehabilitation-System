from django.db import models
from clients.models import Client
from users.models import User

class Appointment(models.Model):
    TYPE_CHOICES = (
        ('checkin', 'Regular Check-in'),
        ('counseling', 'Counseling Session'),
        ('court', 'Court Appearance'),
        ('drug_test', 'Drug Test'),
        ('home_visit', 'Home Visit'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    officer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'officer'})
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    location = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_appointment_type_display()} - {self.client.full_name} - {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"