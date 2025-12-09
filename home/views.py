from django.shortcuts import render, redirect, redirect, get_object_or_404
import csv
from django.http import HttpResponse
from .forms import ProfileForm, MessageForm, GroupConversationForm
import os
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import TreeSubmission, Conversation, Message, CustomUser, Notification
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q # For searching
import json
# class TreeSubmissionForm(forms.ModelForm):
#     class Meta:
#         model = TreeSubmission
#         fields = ['tree_name', 'location', 'description']

def is_moderator(user):
    return user.is_authenticated and user.role == 'moderator'


def google_login_redirect(request):
    """
    Automatically redirects /accounts/login/ to Google's OAuth login.
    """
    return redirect("google_login")

# Create your views here.
def index(request):
    mapbox_token = os.getenv("MAPBOX_TOKEN")
    all_users = []
    is_mod = False
    if request.user.is_authenticated:
        all_users = CustomUser.objects.exclude(id=request.user.id)
        is_mod = request.user.role == 'moderator'

    return render(request, 'home/index.html', {
        'all_users': all_users,
        "MAPBOX_TOKEN": mapbox_token,
        'is_moderator': is_mod
    })

@user_passes_test(is_moderator)
def moderator(request):
    total_users = CustomUser.objects.count()
    flagged_trees = TreeSubmission.objects.filter(is_flagged=True, is_deleted=False).count()
    total_trees = TreeSubmission.objects.filter(is_deleted=False).count()
    total_messages = Message.objects.count()

    return render(request, 'home/moderator.html', {
        'total_users': total_users,
        'pending_trees': flagged_trees,  # Now shows flagged trees count
        'approved_trees': total_trees,   # Now shows total active trees
        'total_messages': total_messages,
    })

@login_required
def first_time_setup(request):
    """Handle first-time user setup with norms and interests"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)

        # Check if user accepted norms
        if 'accept_norms' not in request.POST:
            # Return form with error if norms not accepted
            return render(request, 'home/first_time_setup.html', {
                'form': form,
                'error': 'You must accept the community norms to continue.'
            })

        # Get selected interests
        interests = request.POST.getlist('interests')
        interests_str = ', '.join(interests) if interests else ''

        if form.is_valid():
            user = form.save(commit=False)
            # Save interests to the sustainability_interests field
            user.sustainability_interests = interests_str
            # Mark profile as completed
            user.profile_completed = True
            user.save()
            return redirect("index")  # Redirect to home after setup
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'home/first_time_setup.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile_completed = True
            user.save()
            return redirect("index")  # Redirect to home after profile setup
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'home/profile.html', {'form': form})

@login_required
def account_settings(request):
    return render(request, 'home/account_settings.html')

def conversation_list(request):
    conversations = request.user.conversations.all()
    
    # Calculate unread counts for each conversation
    conversations_with_unread = []
    total_unread = 0
    
    for conversation in conversations:
        # Count unread messages in this conversation
        # Messages where user is NOT the sender AND user is NOT in read_by
        unread_count = conversation.messages.exclude(
            sender=request.user
        ).exclude(
            read_by=request.user
        ).count()
        
        total_unread += unread_count
        
        # Add unread_count as an attribute to the conversation object
        conversation.unread_count = unread_count
        conversations_with_unread.append(conversation)
    
    return render(request, 'home/conversation_list.html', {
        'conversations': conversations_with_unread,
        'total_unread': total_unread
    })

@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)

    if request.user not in conversation.participants.all():
        return HttpResponse("You are not authorized to view this conversation.", status=403)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect('conversation_detail', pk=pk)
    else:
        form = MessageForm()

    messages = conversation.messages.all()
    
    # Mark all messages in this conversation as read by current user
    for message in messages:
        if request.user not in message.read_by.all():
            message.read_by.add(request.user)
    return render(request, 'home/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'form': form
    })

@login_required
def create_conversation(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    )

    if conversation.exists():
        return redirect('conversation_detail', pk=conversation.first().pk)
    else:
        new_conversation = Conversation.objects.create()
        new_conversation.participants.add(request.user, other_user)
        return redirect('conversation_detail', pk=new_conversation.pk)
@login_required
def create_group_conversation(request):
    if request.method == 'POST':
        form = GroupConversationForm(request.POST, user=request.user)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.is_group = True
            conversation.admin = request.user
            conversation.save()
            
            # Add participants
            conversation.participants.set(form.cleaned_data['participants'])
            conversation.participants.add(request.user) # Add creator to participants
            
            return redirect('conversation_detail', pk=conversation.pk)
    else:
        form = GroupConversationForm(user=request.user)
    
    return render(request, 'home/create_group.html', {'form': form})

@login_required
def leave_group(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    
    # Check if it's a group and user is a participant
    if not conversation.is_group:
        return HttpResponse("This is not a group conversation.", status=400)
    
    if request.user not in conversation.participants.all():
        return HttpResponse("You are not a participant in this conversation.", status=403)
    
    # If user is admin, transfer admin to another participant
    if conversation.admin == request.user:
        remaining_participants = conversation.participants.exclude(id=request.user.id)
        if remaining_participants.exists():
            conversation.admin = remaining_participants.first()
            conversation.save()
    
    # Remove user from participants
    conversation.participants.remove(request.user)
    
    return redirect('conversation_list')


def about(request):
    return render(request, 'home/about.html')

from .models import CustomUser

def community(request):
    other_users = []
    conversants = []
    if request.user.is_authenticated:
        other_users = CustomUser.objects.exclude(id=request.user.id)
        conversants = CustomUser.objects.filter(conversations__participants=request.user).exclude(id=request.user.id).distinct()
        for user in other_users:
            user.conversant = user in conversants
    return render(request, 'home/community.html', {'other_users': other_users, "conversants": conversants})

@login_required
@csrf_exempt 
def add_tree(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    species = data.get("species")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    description = data.get("description", "")

    if not all([species, latitude, longitude]):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    tree = TreeSubmission.objects.create(
        user=request.user,
        species=species,
        latitude=latitude,
        longitude=longitude,
        description=description
    )

    return JsonResponse({"success": True, "tree_id": tree.id}, status=201)

@user_passes_test(is_moderator)
def moderate_trees(request):
    # Now shows flagged trees instead of pending trees
    flagged_trees = TreeSubmission.objects.filter(is_flagged=True, is_deleted=False)
    return render(request, 'archive/moderate_trees.html', {'submissions': flagged_trees})

def get_trees(request):
    """API endpoint to fetch all non-deleted trees for map display"""
    trees = TreeSubmission.objects.filter(is_deleted=False)
    trees_data = [
        {
            'id': tree.id,
            'species': tree.species,
            'latitude': tree.latitude,
            'longitude': tree.longitude,
            'description': tree.description,
            'is_flagged': tree.is_flagged,
            'submitted_by': tree.user.get_display_name(),
        }
        for tree in trees
    ]
    return JsonResponse({'trees': trees_data})

def feedback_success(request):
    return render(request, 'home/submission_success.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('index')
    return redirect('account_settings')

@user_passes_test(is_moderator)
@csrf_exempt
def edit_tree(request, tree_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        tree = TreeSubmission.objects.get(id=tree_id)
        data = json.loads(request.body)

        if 'species' in data:
            tree.species = data['species']
        if 'description' in data:
            tree.description = data['description']

        tree.save()
        return JsonResponse({"success": True})
    except TreeSubmission.DoesNotExist:
        return JsonResponse({"error": "Tree not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@user_passes_test(is_moderator)
@csrf_exempt
def delete_tree(request, tree_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        tree = TreeSubmission.objects.get(id=tree_id)
        tree.is_deleted = True  # Soft delete
        tree.save()

        # Create notification for tree owner
        Notification.objects.create(
            recipient=tree.user,
            sender=request.user,
            notification_type='tree_deleted',
            tree_submission=tree,
            message=f"Your {tree.species} tree submission has been removed by a moderator."
        )

        return JsonResponse({"success": True})
    except TreeSubmission.DoesNotExist:
        return JsonResponse({"error": "Tree not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@csrf_exempt
def flag_tree(request, tree_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        reason = data.get('reason', '')

        tree = TreeSubmission.objects.get(id=tree_id)

        # Prevent users from flagging their own trees
        if tree.user == request.user:
            return JsonResponse({"error": "You cannot flag your own tree"}, status=400)

        # Prevent double-flagging
        if tree.is_flagged:
            return JsonResponse({"error": "This tree has already been flagged"}, status=400)

        from django.utils import timezone
        tree.is_flagged = True
        tree.flagged_by = request.user
        tree.flagged_at = timezone.now()
        tree.flag_reason = reason
        tree.save()

        # Create notification for tree owner
        Notification.objects.create(
            recipient=tree.user,
            sender=request.user,
            notification_type='tree_flagged',
            tree_submission=tree,
            message=f"Your {tree.species} tree submission has been flagged for review. Reason: {reason}"
        )

        return JsonResponse({"success": True, "message": "Tree flagged for moderator review"})
    except TreeSubmission.DoesNotExist:
        return JsonResponse({"error": "Tree not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@user_passes_test(is_moderator)
@csrf_exempt
def unflag_tree(request, tree_id):
    """Moderators can unflag a tree (approve it)"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        tree = TreeSubmission.objects.get(id=tree_id)
        tree.is_flagged = False
        tree.flagged_by = None
        tree.flagged_at = None
        tree.flag_reason = ''
        tree.save()

        # Create notification for tree owner
        Notification.objects.create(
            recipient=tree.user,
            sender=request.user,
            notification_type='tree_unflagged',
            tree_submission=tree,
            message=f"Good news! Your {tree.species} tree submission has been reviewed and approved by a moderator."
        )

        return JsonResponse({"success": True, "message": "Tree approved and unflagged"})
    except TreeSubmission.DoesNotExist:
        return JsonResponse({"error": "Tree not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@user_passes_test(is_moderator)
def mod_get_users(request):
    users = CustomUser.objects.all()
    users_data = [
        {
            'id': user.id,
            'username': user.get_display_name(),
            'email': user.email,
            'role': user.role,
            'date_joined': user.date_joined.isoformat(),
            'is_active': user.is_active,
        }
        for user in users
    ]
    return JsonResponse({'users': users_data})

@user_passes_test(is_moderator)
def mod_search_users(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query) | Q(nickname__icontains=query)
    )
    users_data = [
        {
            'id': user.id,
            'username': user.get_display_name(),
            'email': user.email,
            'role': user.role,
        }
        for user in users
    ]
    return JsonResponse({'users': users_data})

@user_passes_test(is_moderator)
@csrf_exempt
def mod_change_role(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        new_role = data.get('role')

        if new_role not in ['user', 'moderator']:
            return JsonResponse({"error": "Invalid role"}, status=400)

        user = CustomUser.objects.get(id=user_id)
        user.role = new_role
        user.save()
        return JsonResponse({"success": True})
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@user_passes_test(is_moderator)
@csrf_exempt
def mod_suspend_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        suspend = data.get('suspend')  # True to suspend, False to reinstate

        # Prevent moderators from suspending themselves
        if user_id == request.user.id:
            return JsonResponse({"error": "You cannot suspend your own account"}, status=400)

        user = CustomUser.objects.get(id=user_id)
        user.is_active = not suspend  # If suspend=True, set is_active=False
        user.save()

        action = "suspended" if suspend else "reinstated"
        return JsonResponse({"success": True, "message": f"User {action} successfully"})
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@user_passes_test(is_moderator)
@csrf_exempt
def mod_delete_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')

        # Prevent moderators from deleting themselves
        if user_id == request.user.id:
            return JsonResponse({"error": "You cannot delete your own account"}, status=400)

        user = CustomUser.objects.get(id=user_id)
        display_name = user.get_display_name()
        user.delete()  # This will cascade delete related data (trees, messages, etc.)

        return JsonResponse({"success": True, "message": f"User {display_name} deleted successfully"})
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@user_passes_test(is_moderator)
def mod_analytics(request):
    from datetime import timedelta
    from django.utils import timezone

    total_users = CustomUser.objects.count()
    seven_days_ago = timezone.now() - timedelta(days=7)
    active_users = CustomUser.objects.filter(last_login__gte=seven_days_ago).count()
    total_trees = TreeSubmission.objects.count()
    total_messages = Message.objects.count()

    return JsonResponse({
        'total_users': total_users,
        'active_users': active_users,
        'total_trees': total_trees,
        'total_messages': total_messages,
    })

@user_passes_test(is_moderator)
def mod_activity(request):
    # Get recent tree submissions and messages
    recent_trees = TreeSubmission.objects.all().order_by('-submitted_at')[:10]
    recent_messages = Message.objects.all().order_by('-timestamp')[:10]

    activities = []

    for tree in recent_trees:
        activities.append({
            'user': tree.user.get_display_name(),
            'action': f'Submitted tree: {tree.species}',
            'time': tree.submitted_at.strftime('%Y-%m-%d %H:%M'),
        })

    for msg in recent_messages:
        activities.append({
            'user': msg.sender.get_display_name(),
            'action': 'Sent a message',
            'time': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
        })

    # Sort by time (descending)
    activities.sort(key=lambda x: x['time'], reverse=True)

    return JsonResponse({'activities': activities[:15]})

@user_passes_test(is_moderator)
def mod_flagged_trees(request):
    """API endpoint to get all flagged trees for moderator review"""
    flagged_trees = TreeSubmission.objects.filter(is_flagged=True, is_deleted=False).order_by('-flagged_at')
    trees_data = [
        {
            'id': tree.id,
            'species': tree.species,
            'latitude': tree.latitude,
            'longitude': tree.longitude,
            'description': tree.description,
            'submitted_by': tree.user.get_display_name(),
            'flagged_by': tree.flagged_by.get_display_name() if tree.flagged_by else 'Unknown',
            'flagged_at': tree.flagged_at.strftime('%Y-%m-%d %H:%M') if tree.flagged_at else '',
            'flag_reason': tree.flag_reason,
        }
        for tree in flagged_trees
    ]
    return JsonResponse({'trees': trees_data})

@user_passes_test(is_moderator)
def mod_tree_stats(request):
    from django.db.models import Count

    flagged = TreeSubmission.objects.filter(is_flagged=True, is_deleted=False).count()
    active = TreeSubmission.objects.filter(is_deleted=False).count()
    deleted = TreeSubmission.objects.filter(is_deleted=True).count()

    # Get species counts for active trees
    species_counts = TreeSubmission.objects.filter(is_deleted=False).values('species').annotate(count=Count('species')).order_by('-count')[:10]

    species_data = [
        {'name': item['species'], 'count': item['count']}
        for item in species_counts
    ]

    return JsonResponse({
        'pending': flagged,     # Now returns flagged trees count
        'approved': active,     # Now returns active (non-deleted) trees
        'rejected': deleted,    # Now returns deleted trees count
        'species': species_data,
    })

@user_passes_test(is_moderator)
def mod_recent_activity(request):
    # Combine different types of activities
    activities = []

    # Recent tree submissions
    recent_trees = TreeSubmission.objects.filter(is_deleted=False).order_by('-submitted_at')[:5]
    for tree in recent_trees:
        status_text = 'flagged' if tree.is_flagged else 'active'
        activities.append({
            'time': tree.submitted_at.strftime('%Y-%m-%d %H:%M'),
            'user': tree.user.get_display_name(),
            'description': f'Submitted {tree.species} tree ({status_text})',
        })

    # Recent user registrations
    recent_users = CustomUser.objects.all().order_by('-date_joined')[:5]
    for user in recent_users:
        activities.append({
            'time': user.date_joined.strftime('%Y-%m-%d %H:%M'),
            'user': user.get_display_name(),
            'description': 'Registered new account',
        })

    # Sort by time
    activities.sort(key=lambda x: x['time'], reverse=True)

    return JsonResponse({'activities': activities[:15]})

def learn(request):
    """Renders the static Learn page with educational resources."""
    return render(request, 'home/learn.html')

@login_required
def export_trees_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="charlottesville_trees.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["ID", "Species", "Description", "Latitude", "Longitude", "Submitted By", "Date"])

    # Query only active (non-deleted) trees
    trees = TreeSubmission.objects.filter(is_deleted=False)

    for tree in trees:
        writer.writerow([
            tree.id,
            tree.species,
            tree.description,
            tree.latitude,
            tree.longitude,
            tree.user.get_display_name(),
            tree.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return response

@login_required
def notifications(request):
    """Display user's notifications"""
    user_notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'home/notifications.html', {
        'notifications': user_notifications
    })

@login_required
@csrf_exempt
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({"success": True})
    except Notification.DoesNotExist:
        return JsonResponse({"error": "Notification not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@csrf_exempt
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@csrf_exempt
def delete_notifications(request):
    """Delete selected notifications for the current user"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])

        if not notification_ids:
            return JsonResponse({"error": "No notifications selected"}, status=400)

        # Delete notifications that belong to the current user
        deleted_count = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user
        ).delete()[0]

        return JsonResponse({
            "success": True,
            "deleted_count": deleted_count
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def get_notifications(request):
    """API endpoint to get user's notifications"""
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': []})

    notifications = Notification.objects.filter(recipient=request.user)
    notifications_data = [
        {
            'id': notif.id,
            'type': notif.notification_type,
            'message': notif.message,
            'is_read': notif.is_read,
            'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M'),
            'sender': notif.sender.get_display_name() if notif.sender else 'System',
        }
        for notif in notifications
    ]
    return JsonResponse({'notifications': notifications_data})