from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('moderator/', views.moderator, name='moderator'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('community/', views.community, name='community'),
    path('submit-tree/', views.submit_tree, name='submit_tree'),
    path('moderate/', views.moderate_trees, name='moderate_trees'),
    path('submission-success/', views.feedback_success, name='submission_success')
]