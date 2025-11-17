from django import forms
from .models import Court, CourtCase, Hearing, CourtOrder

class CourtForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ['name', 'court_type', 'address', 'phone', 'email', 'clerk_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter court name'}),
            'court_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter court address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'clerk_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter clerk name'}),
        }
        labels = {
            'clerk_name': 'Court Clerk Name',
        }

class CourtCaseForm(forms.ModelForm):
    class Meta:
        model = CourtCase
        fields = ['case', 'court', 'judge', 'case_number', 'filing_date', 'next_hearing_date', 'status', 'notes']
        widgets = {
            'case': forms.Select(attrs={'class': 'form-control'}),
            'court': forms.Select(attrs={'class': 'form-control'}),
            'judge': forms.Select(attrs={'class': 'form-control'}),
            'case_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter case number'}),
            'filing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_hearing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter case notes'}),
        }

class HearingForm(forms.ModelForm):
    class Meta:
        model = Hearing
        fields = ['court_case', 'hearing_type', 'hearing_date', 'judge', 'location', 'notes']
        widgets = {
            'court_case': forms.Select(attrs={'class': 'form-control'}),
            'hearing_type': forms.Select(attrs={'class': 'form-control'}),
            'hearing_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'judge': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hearing location'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter hearing notes'}),
        }

class CourtOrderForm(forms.ModelForm):
    class Meta:
        model = CourtOrder
        fields = ['court_case', 'order_type', 'order_date', 'effective_date', 'judge', 'order_text', 'file']
        widgets = {
            'court_case': forms.Select(attrs={'class': 'form-control'}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'judge': forms.Select(attrs={'class': 'form-control'}),
            'order_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter order text'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        