from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.BigIntegerField(null=True)  # OID for profile picture
    
    def __str__(self):
        return f"{self.user.username}'s profile"
