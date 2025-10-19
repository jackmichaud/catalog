from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.decorators import user_passes_test, login_required

def is_moderator(user):
    return user.is_authenticated and user.role == 'moderator'


# Create your views here.
def index(request):
    return render(request, 'home/index.html')

@user_passes_test(is_moderator)
def moderator(request):
    return render(request, 'home/moderator.html')

@login_required
def profile(request):
    return render(request, 'home/profile.html')
