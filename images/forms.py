from django import forms
from .models import Image

class ImageUploadForm(forms.ModelForm):
    image_file = forms.ImageField(required=True)
    
    class Meta:
        model = Image
        fields = ['title', 'description']
