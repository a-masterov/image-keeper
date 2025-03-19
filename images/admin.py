from django.contrib import admin
from .models import Image

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'uploaded_at', 'file_size')
    list_filter = ('uploaded_at', 'owner')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('id', 'uploaded_at', 'image_oid', 'file_size', 'content_type')
