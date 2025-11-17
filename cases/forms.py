from django import forms
from .models import Case, RehabilitationPlan, PlanItem

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['client', 'officer', 'presiding_judge', 'status', 'court_type', 
                 'case_number', 'opening_date', 'closing_date', 'sentencing_date',
                 'next_court_date', 'objectives', 'special_conditions', 'court_notes',
                 'is_high_profile']
        widgets = {
            'opening_date': forms.DateInput(attrs={'type': 'date'}),
            'closing_date': forms.DateInput(attrs={'type': 'date'}),
            'sentencing_date': forms.DateInput(attrs={'type': 'date'}),
            'next_court_date': forms.DateInput(attrs={'type': 'date'}),
            'objectives': forms.Textarea(attrs={'rows': 4}),
            'special_conditions': forms.Textarea(attrs={'rows': 3}),
            'court_notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show officers in the officer field
        from users.models import User
        self.fields['officer'].queryset = User.objects.filter(
            user_type='officer', 
            is_active_officer=True
        )
        # Only show judges in the presiding_judge field
        self.fields['presiding_judge'].queryset = User.objects.filter(
            user_type='judge'
        )

class RehabilitationPlanForm(forms.ModelForm):
    class Meta:
        model = RehabilitationPlan
        fields = ['title', 'description', 'start_date', 'end_date', 'judicial_review_required']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PlanItemForm(forms.ModelForm):
    class Meta:
        model = PlanItem
        fields = ['description', 'due_date', 'notes', 'requires_judicial_review']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }