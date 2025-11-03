from django.shortcuts import render, redirect, redirect
from django.http import HttpResponse
from .forms import ProfileForm
import os
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import TreeSubmission
from django import forms

class TreeSubmissionForm(forms.ModelForm):
    class Meta:
        model = TreeSubmission
        fields = ['tree_name', 'location', 'description']

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
def submit_tree(request):
    if request.method == 'POST':
        form = TreeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            return redirect('submission_success')
    else:
        form = TreeSubmissionForm()

    return render(request, 'home/submit_tree.html', {'form': form})

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
