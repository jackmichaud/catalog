from django.shortcuts import render, redirect, redirect
from django.http import HttpResponse
from .forms import ProfileForm
import os
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import TreeSubmission
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
# class TreeSubmissionForm(forms.ModelForm):
#     class Meta:
#         model = TreeSubmission
#         fields = ['tree_name', 'location', 'description']

def is_moderator(user):
    return user.is_authenticated and user.role == 'moderator'


# Create your views here.
def index(request):
    mapbox_token = os.getenv("MAPBOX_TOKEN")
    return render(request, 'home/index.html', {"MAPBOX_TOKEN": mapbox_token})

@user_passes_test(is_moderator)
def moderator(request):
    return render(request, 'home/moderator.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            print("req.f", request.FILES)  # Should show the UploadedFile object
            print(form.cleaned_data['avatar'])  # Should be an InMemoryUploadedFile
            form.save()
            return redirect(".")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'home/profile.html', {'form': form})

@user_passes_test(is_moderator)
def moderator(request):
    return render(request, 'home/moderator.html')

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
