from django.db import models
from clients.models import Client
from users.models import User
from django.utils import timezone

class Case(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending Review'),
        ('sentenced', 'Sentenced'),
        ('appealed', 'Appealed'),
    )
    
    COURT_CHOICES = (
        ('supreme', 'Supreme Court'),
        ('high', 'High Court'),
        ('circuit', 'Circuit Court'),
        ('district', 'District Court'),
        ('family', 'Family Court'),
        ('drug', 'Drug Court'),
        ('juvenile', 'Juvenile Court'),
    )
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cases')
    
    # FIX: Add unique related_name for both officer and presiding_judge
    officer = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        limit_choices_to={'user_type': 'officer'},
        related_name='officer_cases'  # Unique related_name
    )
    
    presiding_judge = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='presiding_cases',
        limit_choices_to={'user_type': 'judge'},
        null=True,
        blank=True
    )
    court_case = models.OneToOneField(
        'courts.CourtCase', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='rehabilitation_case'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    court_type = models.CharField(max_length=20, choices=COURT_CHOICES, default='circuit')
    case_number = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Court case number
    opening_date = models.DateField(default=timezone.now)
    closing_date = models.DateField(null=True, blank=True)
    sentencing_date = models.DateField(null=True, blank=True)
    next_court_date = models.DateField(null=True, blank=True)
    objectives = models.TextField()
    special_conditions = models.TextField(blank=True)
    court_notes = models.TextField(blank=True)  # Judge's notes
    is_high_profile = models.BooleanField(default=False)  # High-profile cases
    
    def __str__(self):
        return f"Case: {self.client.full_name} ({self.case_number})"
    
    @property
    def days_until_court(self):
        """Calculate days until next court date"""
        if self.next_court_date:
            delta = self.next_court_date - timezone.now().date()
            return delta.days
        return None
     # Add method to check if case has court proceedings
    def has_court_proceedings(self):
        return hasattr(self, 'court_case') and self.court_case is not None
    
    # Add method to get next court date
    def get_next_court_date(self):
        if self.has_court_proceedings():
            return self.court_case.next_hearing_date
        return None
    
    class Meta:
        ordering = ['-opening_date']

class RehabilitationPlan(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='rehabilitation_plans')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    judicial_review_required = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.case.client.full_name}"
    
    @property
    def progress_percentage(self):
        total_items = self.plan_items.count()
        if total_items == 0:
            return 0
        completed_items = self.plan_items.filter(is_completed=True).count()
        return (completed_items / total_items) * 100

class PlanItem(models.Model):
    rehabilitation_plan = models.ForeignKey(RehabilitationPlan, on_delete=models.CASCADE, related_name='plan_items')
    description = models.TextField()
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    requires_judicial_review = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.description[:50]}..."