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

class TreeSubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    species = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.species} ({self.latitude}, {self.longitude})"