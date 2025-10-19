from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('moderator/', views.moderator, name='moderator'),
    path('profile/', views.profile, name='profile')
]