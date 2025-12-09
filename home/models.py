from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from storages.backends.s3boto3 import S3Boto3Storage

s3_storage = S3Boto3Storage()

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', storage=s3_storage, null=True, blank=True)
    bio = models.TextField(blank=True)
    sustainability_interests = models.CharField(max_length=255, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    profile_completed = models.BooleanField(default=False)

    def get_display_name(self):
        """Return nickname if set, otherwise username"""
        return self.nickname if self.nickname else self.username

class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations"
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    is_group = models.BooleanField(default=False)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="admin_conversations"
    )

    def __str__(self):
        return ", ".join([user.get_display_name() for user in self.participants.all()])

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    image_attachment = models.ImageField(
        upload_to='message_attachments/', storage=s3_storage, blank=True, null=True
    )
    
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="read_messages", blank=True
    )

    class Meta:
        ordering = ['timestamp'] 

    def __str__(self):
        return f"Message from {self.sender.get_display_name()} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class TreeSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    species = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='flagged_trees')
    flagged_at = models.DateTimeField(null=True, blank=True)
    flag_reason = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.species} ({self.latitude}, {self.longitude})"