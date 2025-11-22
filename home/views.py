from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProfileForm
import os
from django.contrib.auth.decorators import user_passes_test, login_required

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

from .models import CustomUser

def community(request):
    users = CustomUser.objects.all()
    return render(request, 'home/community.html', {'users': users})
