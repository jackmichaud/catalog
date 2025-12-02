from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('moderator/', views.moderator, name='moderator'),
    path('profile/', views.profile, name='profile'),
    path('account-settings/', views.account_settings, name='account_settings'),
    path('about/', views.about, name='about'),
    path('messages/', views.conversation_list, name='conversation_list'),
    path('messages/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('messages/new/<int:user_id>/', views.create_conversation, name='create_conversation'),
    path('community/', views.community, name='community'),
    # path('submit-tree/', views.submit_tree, name='submit_tree'),
    path('moderate/', views.moderate_trees, name='moderate_trees'),
    # path('submission-success/', views.feedback_success, name='submission_success'),
    path("api/trees/add/", views.add_tree, name="add_tree"),
    path("api/trees/", views.get_trees, name="get_trees"),
    path('delete-account/', views.delete_account, name='delete_account'),
]