from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm

@login_required
def appointment_list(request):
    today = timezone.now().date()
    appointments = Appointment.objects.filter(scheduled_date__date=today).order_by('scheduled_date')
    upcoming = Appointment.objects.filter(scheduled_date__date__gt=today).order_by('scheduled_date')[:10]
    
    context = {
        'appointments_today': appointments,
        'upcoming_appointments': upcoming
    }
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.officer = request.user
            appointment.save()
            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Schedule Appointment'})

@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Edit Appointment'})

@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully!')
        return redirect('appointment_list')
    
    return render(request, 'appointments/appointment_confirm_delete.html', {'appointment': appointment})