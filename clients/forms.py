from django import forms
from .models import Client, Address, Offense

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['case_number', 'first_name', 'last_name', 'date_of_birth', 
                 'gender', 'assigned_officer', 'status', 'start_date', 
                 'end_date', 'risk_level', 'notes']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Only show active probation officers in the assigned officer field
        from users.models import User
        self.fields['assigned_officer'].queryset = User.objects.filter(
            user_type='officer', 
            is_active_officer=True
        ).order_by('first_name', 'last_name')
        
        # Add helpful labels and placeholders
        self.fields['assigned_officer'].label = "Assign to Probation Officer"
        self.fields['assigned_officer'].empty_label = "Select a Probation Officer"

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_type', 'street', 'city', 'state', 'zip_code', 'is_primary']

class OffenseForm(forms.ModelForm):
    class Meta:
        model = Offense
        fields = ['offense_type', 'description', 'date_committed', 'sentence', 'court']
        widgets = {
            'date_committed': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }