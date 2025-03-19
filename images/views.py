from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.db import transaction
from .models import Image
from .forms import ImageUploadForm
from .utils import store_image_as_lo, retrieve_image_as_lo, delete_image_lo

@login_required
def image_list(request):
    images = Image.objects.all()
    return render(request, 'images/image_list.html', {'images': images})

@login_required
def image_detail(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    return render(request, 'images/image_detail.html', {'image': image})

@login_required
def image_upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded file
            image_file = request.FILES.get('image_file')
            
            if not image_file:
                messages.error(request, 'No image file provided.')
                return redirect('image_upload')
            
            # Check if it's a JPEG
            if not image_file.content_type.startswith('image/jpeg'):
                messages.error(request, 'Only JPEG images are allowed.')
                return redirect('image_upload')
            
            # Create image instance but don't save to DB yet
            image = form.save(commit=False)
            image.owner = request.user
            image.content_type = image_file.content_type
            image.file_size = image_file.size
            
            # Read the file data
            image_data = image_file.read()
            
            # Store the image as a large object in PostgreSQL
            with transaction.atomic():
                # Store the image data in a large object
                oid = store_image_as_lo(image_data)
                
                # Save the OID in the image model
                image.image_oid = oid
                image.save()
            
            messages.success(request, 'Image uploaded successfully!')
            return redirect('image_detail', image_id=image.id)
    else:
        form = ImageUploadForm()
    
    return render(request, 'images/image_upload.html', {'form': form})

@login_required
def image_download(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    
    # Retrieve the image data from the large object
    image_data = retrieve_image_as_lo(image.image_oid)
    
    if not image_data:
        raise Http404("Image data not found")
    
    # Create a response with the image data
    response = HttpResponse(image_data, content_type=image.content_type)
    response['Content-Disposition'] = f'attachment; filename="{image.title}.jpg"'
    
    return response

@login_required
def image_view(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    
    # Retrieve the image data from the large object
    image_data = retrieve_image_as_lo(image.image_oid)
    
    if not image_data:
        raise Http404("Image data not found")
    
    # Create a response with the image data
    response = HttpResponse(image_data, content_type=image.content_type)
    
    return response

@login_required
def image_delete(request, image_id):
    image = get_object_or_404(Image, id=image_id, owner=request.user)
    
    if request.method == 'POST':
        # Delete the large object
        delete_image_lo(image.image_oid)
        
        # Delete the image record
        image.delete()
        
        messages.success(request, 'Image deleted successfully!')
        return redirect('image_list')
    
    return render(request, 'images/image_confirm_delete.html', {'image': image})
