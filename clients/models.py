from django.db import models
from users.models import User

class Client(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('violated', 'Violated'),
        ('transferred', 'Transferred'),
    )
    
    # Client identification (NO USER LINK - they don't login)
    case_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Management fields (only staff/officers manage these)
    assigned_officer = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'user_type': 'officer', 'is_active_officer': True})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField()
    end_date = models.DateField()
    risk_level = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='clients_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.case_number})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Address(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=[('home', 'Home'), ('work', 'Work')])
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.client.full_name} - {self.address_type}"

class Offense(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='offenses')
    offense_type = models.CharField(max_length=255)
    description = models.TextField()
    date_committed = models.DateField()
    sentence = models.CharField(max_length=255)
    court = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.client.full_name} - {self.offense_type}"