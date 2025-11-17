from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'System Administrator'),
        ('officer', 'Probation Officer'),
        ('staff', 'Support Staff'),
        ('judge', 'Judge'),
    )  
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='officer')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    badge_number = models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    is_active_officer = models.BooleanField(default=True)  # Track if officer is active
    court_jurisdiction = models.CharField(max_length=100, blank=True)  # For judges
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    def can_manage_clients(self):
        """Check if user can manage clients"""
        return self.user_type in ['admin', 'officer', 'staff']
    
    def can_add_clients(self):
        """Check if user can add clients"""
        return self.user_type in ['admin', 'officer', 'staff']
    
    def can_delete_clients(self):
        """Check if user can delete clients"""
        return self.user_type == 'admin'
    
    def is_probation_officer(self):
        """Check if user is an active probation officer"""
        return self.user_type == 'officer' and self.is_active_officer
    def is_judge(self):
        """Check if user is a judge"""
        return self.user_type == 'judge'
    def can_view_court_cases(self):
        """Check if user can view court cases"""
        return self.user_type in ['admin', 'judge', 'officer']
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"