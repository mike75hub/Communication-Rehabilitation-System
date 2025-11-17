from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Message, Notification
from .forms import MessageForm

@login_required
def message_list(request):
    messages_list = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-sent_at')
    
    unread_count = Message.objects.filter(
        recipient=request.user,
        read_at__isnull=True
    ).count()
    
    context = {
        'messages': messages_list,
        'unread_count': unread_count
    }
    return render(request, 'comms/message_list.html', context)

@login_required
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)
    
    # Mark as read if recipient
    if message.recipient == request.user and not message.read_at:
        message.read_at = timezone.now()
        message.save()
    
    context = {
        'message': message
    }
    return render(request, 'comms/message_detail.html', context)

@login_required
def message_create(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('message_list')
    else:
        form = MessageForm()
    
    return render(request, 'comms/message_form.html', {'form': form})

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'comms/notification_list.html', context)

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    return redirect('notification_list')