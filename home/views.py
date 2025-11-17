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
    if request.user.is_authenticated:
        all_users = CustomUser.objects.exclude(id=request.user.id)

    return render(request, 'home/index.html', {'all_users': all_users, "MAPBOX_TOKEN": mapbox_token})

@user_passes_test(is_moderator)
def moderator(request):
    return render(request, 'home/moderator.html')

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

def community(request):
    return render(request, 'home/community.html')

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

    return render(request, 'moderate_trees.html', {'submissions': submissions})

def feedback_success(request):
    return render(request, 'home/submission_success.html')
