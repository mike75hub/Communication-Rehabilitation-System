from django.db import models
from django.conf import settings
from django.utils import timezone

class Court(models.Model):
    COURT_TYPES = [
        ('SUPERIOR', 'Superior Court'),
        ('DISTRICT', 'District Court'),
        ('JUVENILE', 'Juvenile Court'),
        ('DRUG', 'Drug Court'),
        ('FEDERAL', 'Federal Court'),
    ]
    
    name = models.CharField(max_length=200)
    court_type = models.CharField(max_length=20, choices=COURT_TYPES)
    address = models.TextField()
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    clerk_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'courts'
    
    def __str__(self):
        return f"{self.name} ({self.get_court_type_display()})"

class CourtCase(models.Model):
    CASE_STATUS = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('APPEALED', 'Appealed'),
    ]
    
    case = models.OneToOneField('cases.Case', on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    judge = models.ForeignKey('judges.Judge', on_delete=models.SET_NULL, null=True, blank=True)
    case_number = models.CharField(max_length=50, unique=True)
    filing_date = models.DateField()
    next_hearing_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=CASE_STATUS, default='PENDING')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'court_cases'
    
    def __str__(self):
        return f"{self.case_number} - {self.court.name}"

class Hearing(models.Model):
    HEARING_TYPES = [
        ('ARRAIGNMENT', 'Arraignment'),
        ('PRETRIAL', 'Pre-trial Conference'),
        ('MOTION', 'Motion Hearing'),
        ('TRIAL', 'Trial'),
        ('SENTENCING', 'Sentencing'),
        ('REVIEW', 'Review Hearing'),
        ('VIOLATION', 'Violation Hearing'),
    ]
    
    court_case = models.ForeignKey(CourtCase, on_delete=models.CASCADE)
    hearing_type = models.CharField(max_length=20, choices=HEARING_TYPES)
    hearing_date = models.DateTimeField()
    judge = models.ForeignKey('judges.Judge', on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'hearings'
        ordering = ['hearing_date']
    
    def __str__(self):
        return f"{self.get_hearing_type_display()} - {self.hearing_date.strftime('%Y-%m-%d')}"

class CourtOrder(models.Model):
    ORDER_TYPES = [
        ('SENTENCE', 'Sentence'),
        ('PROBATION', 'Probation Order'),
        ('TERMINATION', 'Probation Termination'),
        ('MODIFICATION', 'Order Modification'),
        ('WARRANT', 'Bench Warrant'),
        ('OTHER', 'Other'),
    ]
    
    court_case = models.ForeignKey(CourtCase, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    order_date = models.DateField()
    effective_date = models.DateField()
    judge = models.ForeignKey('judges.Judge', on_delete=models.CASCADE)
    order_text = models.TextField()
    file = models.FileField(upload_to='court_orders/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'court_orders'
    
    def __str__(self):
        return f"{self.get_order_type_display()} - {self.order_date}"