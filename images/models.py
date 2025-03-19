from django.db import models
from django.contrib.auth.models import User
import uuid

class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    
    # This field will store the OID of the large object in PostgreSQL
    # or a file ID for SQLite
    image_oid = models.CharField(max_length=255, null=True)
    
    # Thumbnail OID for faster gallery loading
    thumbnail_oid = models.CharField(max_length=255, null=True)
    
    # Metadata for the image
    content_type = models.CharField(max_length=100, default='image/jpeg')
    file_size = models.BigIntegerField(default=0)
    
    def __str__(self):
        return self.title
