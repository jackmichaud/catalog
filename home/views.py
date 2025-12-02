from django.shortcuts import render, redirect, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import ProfileForm, MessageForm
import os
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import TreeSubmission, Conversation, Message, CustomUser
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
    pending_trees = TreeSubmission.objects.filter(status='pending').count()
    approved_trees = TreeSubmission.objects.filter(status='approved').count()
    total_messages = Message.objects.count()

    return render(request, 'home/moderator.html', {
        'total_users': total_users,
        'pending_trees': pending_trees,
        'approved_trees': approved_trees,
        'total_messages': total_messages,
    })

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            print("req.f", request.FILES)
            print(form.cleaned_data['avatar'])
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'home/profile.html', {'form': form})

@login_required
def account_settings(request):
    return render(request, 'home/account_settings.html')

@login_required
def conversation_list(request):
    conversations = request.user.conversations.all()
    return render(request, 'home/conversation_list.html', {'conversations': conversations})

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
    submissions = TreeSubmission.objects.filter(status='pending')

    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        action = request.POST.get('action')

        submission = TreeSubmission.objects.get(id=submission_id)
        if action == 'approve':
            submission.status = 'approved'
        elif action == 'reject':
            submission.status = 'rejected'
        submission.save()

    return render(request, 'archive/moderate_trees.html', {'submissions': submissions})

def get_trees(request):
    """API endpoint to fetch all approved trees for map display"""
    approved_trees = TreeSubmission.objects.filter(status='approved')
    trees_data = [
        {
            'id': tree.id,
            'species': tree.species,
            'latitude': tree.latitude,
            'longitude': tree.longitude,
            'description': tree.description,
        }
        for tree in approved_trees
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
        tree.delete()
        return JsonResponse({"success": True})
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
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'date_joined': user.date_joined.isoformat(),
        }
        for user in users
    ]
    return JsonResponse({'users': users_data})

@user_passes_test(is_moderator)
def mod_search_users(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    )
    users_data = [
        {
            'id': user.id,
            'username': user.username,
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
            'user': tree.user.username,
            'action': f'Submitted tree: {tree.species}',
            'time': tree.submitted_at.strftime('%Y-%m-%d %H:%M'),
        })

    for msg in recent_messages:
        activities.append({
            'user': msg.sender.username,
            'action': 'Sent a message',
            'time': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
        })

    # Sort by time (descending)
    activities.sort(key=lambda x: x['time'], reverse=True)

    return JsonResponse({'activities': activities[:15]})

@user_passes_test(is_moderator)
def mod_tree_stats(request):
    from django.db.models import Count

    pending = TreeSubmission.objects.filter(status='pending').count()
    approved = TreeSubmission.objects.filter(status='approved').count()
    rejected = TreeSubmission.objects.filter(status='rejected').count()

    # Get species counts
    species_counts = TreeSubmission.objects.filter(status='approved').values('species').annotate(count=Count('species')).order_by('-count')[:10]

    species_data = [
        {'name': item['species'], 'count': item['count']}
        for item in species_counts
    ]

    return JsonResponse({
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'species': species_data,
    })

@user_passes_test(is_moderator)
def mod_recent_activity(request):
    # Combine different types of activities
    activities = []

    # Recent tree submissions
    recent_trees = TreeSubmission.objects.all().order_by('-submitted_at')[:5]
    for tree in recent_trees:
        activities.append({
            'time': tree.submitted_at.strftime('%Y-%m-%d %H:%M'),
            'user': tree.user.username,
            'description': f'Submitted {tree.species} tree ({tree.status})',
        })

    # Recent user registrations
    recent_users = CustomUser.objects.all().order_by('-date_joined')[:5]
    for user in recent_users:
        activities.append({
            'time': user.date_joined.strftime('%Y-%m-%d %H:%M'),
            'user': user.username,
            'description': 'Registered new account',
        })

    # Sort by time
    activities.sort(key=lambda x: x['time'], reverse=True)

    return JsonResponse({'activities': activities[:15]})
