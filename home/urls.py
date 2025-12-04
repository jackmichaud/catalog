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
    path('create_group/', views.create_group_conversation, name='create_group_conversation'),
    path('messages/<int:pk>/leave/', views.leave_group, name='leave_group'),
    # path('submit-tree/', views.submit_tree, name='submit_tree'),
    path('moderate/', views.moderate_trees, name='moderate_trees'),
    # path('submission-success/', views.feedback_success, name='submission_success'),
    path("api/trees/add/", views.add_tree, name="add_tree"),
    path("api/trees/", views.get_trees, name="get_trees"),
    path("api/trees/<int:tree_id>/edit/", views.edit_tree, name="edit_tree"),
    path("api/trees/<int:tree_id>/delete/", views.delete_tree, name="delete_tree"),
    path('delete-account/', views.delete_account, name='delete_account'),
    # Moderator API endpoints
    path('moderator/api/users/', views.mod_get_users, name='mod_get_users'),
    path('moderator/api/users/search/', views.mod_search_users, name='mod_search_users'),
    path('moderator/api/users/change-role/', views.mod_change_role, name='mod_change_role'),
    path('moderator/api/users/suspend/', views.mod_suspend_user, name='mod_suspend_user'),
    path('moderator/api/users/delete/', views.mod_delete_user, name='mod_delete_user'),
    path('moderator/api/analytics/', views.mod_analytics, name='mod_analytics'),
    path('moderator/api/activity/', views.mod_activity, name='mod_activity'),
    path('moderator/api/tree-stats/', views.mod_tree_stats, name='mod_tree_stats'),
    path('moderator/api/recent-activity/', views.mod_recent_activity, name='mod_recent_activity'),
]