from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Judge(models.Model):
    COURT_TYPES = [
        ('SUPERIOR', 'Superior Court'),
        ('DISTRICT', 'District Court'),
        ('JUVENILE', 'Juvenile Court'),
        ('DRUG', 'Drug Court'),
        ('FEDERAL', 'Federal Court'),
        ('APPEALS', 'Court of Appeals'),
    ]
    
    SPECIALIZATIONS = [
        ('CRIMINAL', 'Criminal Law'),
        ('FAMILY', 'Family Law'),
        ('JUVENILE', 'Juvenile Law'),
        ('DRUG', 'Drug Court'),
        ('MENTAL_HEALTH', 'Mental Health'),
        ('VETERANS', 'Veterans Court'),
        ('TRAFFIC', 'Traffic Court'),
        ('CIVIL', 'Civil Law'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='judge_profile'
    )
    judge_id = models.CharField(max_length=20, unique=True, verbose_name="Judge ID")
    court = models.ForeignKey('courts.Court', on_delete=models.SET_NULL, null=True, blank=True, related_name='judges')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATIONS, default='CRIMINAL')
    appointment_date = models.DateField()
    phone = models.CharField(max_length=15, blank=True)
    office_location = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True, verbose_name="Biography")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'judges'
        verbose_name = 'Judge'
        verbose_name_plural = 'Judges'
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"Hon. {self.user.get_full_name()} ({self.judge_id})"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def get_email(self):
        return self.user.email
    
    def get_upcoming_hearings(self, days=30):
        """Get upcoming hearings for this judge"""
        from courts.models import Hearing
        return Hearing.objects.filter(
            judge=self,
            hearing_date__gte=timezone.now(),
            hearing_date__lte=timezone.now() + timedelta(days=days)
        ).order_by('hearing_date')
    
    def get_active_court_cases(self):
        """Get active court cases for this judge"""
        from courts.models import CourtCase
        return CourtCase.objects.filter(judge=self, status='ACTIVE')
    
    def get_pending_orders(self):
        """Get pending orders for this judge"""
        from courts.models import CourtOrder
        return CourtOrder.objects.filter(judge=self, is_active=True)
    
    def get_caseload_count(self):
        """Get number of active cases assigned to this judge"""
        return self.get_active_court_cases().count()
    
    def get_hearing_count_today(self):
        """Get number of hearings scheduled for today"""
        from courts.models import Hearing
        today = timezone.now().date()
        return Hearing.objects.filter(
            judge=self,
            hearing_date__date=today
        ).count()
    
    def get_judicial_experience_years(self):
        """Calculate years of judicial experience"""
        if self.appointment_date:
            today = timezone.now().date()
            experience = today.year - self.appointment_date.year
            if today.month < self.appointment_date.month or (
                today.month == self.appointment_date.month and today.day < self.appointment_date.day
            ):
                experience -= 1
            return max(0, experience)
        return 0

class CourtAssignment(models.Model):
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE, related_name='court_assignments')
    court = models.ForeignKey('courts.Court', on_delete=models.CASCADE, related_name='judge_assignments')
    assignment_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    assignment_type = models.CharField(max_length=20, choices=[
        ('PERMANENT', 'Permanent'),
        ('TEMPORARY', 'Temporary'),
        ('VISITING', 'Visiting Judge'),
        ('SENIOR', 'Senior Status'),
    ], default='PERMANENT')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'court_assignments'
        verbose_name = 'Court Assignment'
        verbose_name_plural = 'Court Assignments'
        unique_together = ['judge', 'court', 'assignment_date']
        ordering = ['-assignment_date']
    
    def __str__(self):
        return f"{self.judge} - {self.court} ({self.assignment_date})"
    
    def is_current(self):
        """Check if this assignment is currently active"""
        today = timezone.now().date()
        if self.end_date:
            return self.assignment_date <= today <= self.end_date
        return self.assignment_date <= today

class JudicialLeave(models.Model):
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=50, choices=[
        ('VACATION', 'Vacation'),
        ('SICK', 'Sick Leave'),
        ('CONFERENCE', 'Conference'),
        ('TRAINING', 'Judicial Training'),
        ('PERSONAL', 'Personal Leave'),
        ('OTHER', 'Other'),
    ])
    reason = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'judicial_leaves'
        verbose_name = 'Judicial Leave'
        verbose_name_plural = 'Judicial Leaves'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.judge} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def is_current(self):
        """Check if the judge is currently on leave"""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.is_approved

# Signal to create judge profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_judge_profile(sender, instance, created, **kwargs):
    """
    Create judge profile when a user is created with judge role.
    You'll need to implement your own logic to determine if a user should be a judge.
    """
    # Example logic - you might have a field like is_judge on your custom user model
    # or use groups to determine judge status
    if created:
        # Don't automatically create judge profiles
        # Judges should be created through admin or specific views
        pass