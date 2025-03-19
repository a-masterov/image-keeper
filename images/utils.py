import os
import psycopg2
from django.db import connection
from django.conf import settings
import base64
from io import BytesIO
from PIL import Image as PILImage

# Create a directory to store images for SQLite mode
IMAGES_DIR = os.path.join(settings.MEDIA_ROOT, 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

# Create a directory for thumbnails in SQLite mode
THUMBNAILS_DIR = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
os.makedirs(THUMBNAILS_DIR, exist_ok=True)

def is_postgres():
    """Check if we're using PostgreSQL"""
    return 'postgresql' in settings.DATABASES['default']['ENGINE']

def store_image_as_lo(image_data):
    """
    Store image data as a PostgreSQL Large Object and return the OID
    or store in filesystem for SQLite
    """
    if is_postgres():
        # Use atomic transaction to ensure we have a transaction context
        from django.db import transaction
        
        with transaction.atomic():
            conn = connection.connection
            # Create a large object
            lobject = conn.lobject(0, 'wb')
            oid = lobject.oid
            
            # Write data to the large object
            lobject.write(image_data)
            lobject.close()
            
            return oid
    else:
        # For SQLite, store the image in the filesystem and return a unique ID
        import uuid
        file_id = str(uuid.uuid4())
        file_path = os.path.join(IMAGES_DIR, f"{file_id}.jpg")
        
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        return file_id

def retrieve_image_as_lo(oid):
    """
    Retrieve image data from a PostgreSQL Large Object by OID
    or from filesystem for SQLite
    """
    if is_postgres():
        # Convert string OID to integer for PostgreSQL
        try:
            oid_int = int(oid) if isinstance(oid, str) else oid
        except (ValueError, TypeError):
            return None
            
        # Use atomic transaction to ensure we have a transaction context
        from django.db import transaction
        
        with transaction.atomic():
            conn = connection.connection
            try:
                lobject = conn.lobject(oid_int, 'rb')
                data = lobject.read()
                lobject.close()
                return data
            except (psycopg2.errors.InvalidParameterValue, AttributeError, psycopg2.ProgrammingError):
                # Handle case where the large object doesn't exist
                return None
    else:
        # For SQLite, retrieve the image from the filesystem
        try:
            file_path = os.path.join(IMAGES_DIR, f"{oid}.jpg")
            with open(file_path, 'rb') as f:
                return f.read()
        except (FileNotFoundError, TypeError):
            return None

def delete_image_lo(oid):
    """
    Delete a PostgreSQL Large Object by OID
    or delete from filesystem for SQLite
    """
    if not oid:
        return
        
    if is_postgres():
        # Convert string OID to integer for PostgreSQL
        try:
            oid_int = int(oid) if isinstance(oid, str) else oid
        except (ValueError, TypeError):
            return
            
        # Use atomic transaction to ensure we have a transaction context
        from django.db import transaction
        
        with transaction.atomic():
            conn = connection.connection
            try:
                lobject = conn.lobject(oid_int, 'wb')
                lobject.unlink()
            except (psycopg2.errors.InvalidParameterValue, AttributeError, psycopg2.ProgrammingError):
                # Handle case where the large object doesn't exist
                pass
    else:
        # For SQLite, delete the image from the filesystem
        try:
            file_path = os.path.join(IMAGES_DIR, f"{oid}.jpg")
            if os.path.exists(file_path):
                os.remove(file_path)
        except (FileNotFoundError, TypeError):
            pass
            
def generate_thumbnail(image_data, max_size=(200, 200)):
    """
    Generate a thumbnail from image data
    """
    try:
        # Open the image from binary data
        img = PILImage.open(BytesIO(image_data))
        
        # Create a thumbnail
        img.thumbnail(max_size)
        
        # Save the thumbnail to a BytesIO object
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=85)
        thumb_io.seek(0)
        
        # Return the thumbnail data
        return thumb_io.read()
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None
        
def generate_thumbnails_for_existing_images():
    """
    Generate thumbnails for all existing images that don't have thumbnails
    """
    from django.db import transaction
    from .models import Image
    
    # Get all images without thumbnails
    images = Image.objects.filter(thumbnail_oid__isnull=True)
    
    for image in images:
        # Skip if no image_oid
        if not image.image_oid:
            continue
            
        # Get the original image data
        image_data = retrieve_image_as_lo(image.image_oid)
        if not image_data:
            continue
            
        # Generate thumbnail
        thumbnail_data = generate_thumbnail(image_data)
        if not thumbnail_data:
            continue
            
        # Store thumbnail
        with transaction.atomic():
            thumbnail_oid = store_image_as_lo(thumbnail_data)
            image.thumbnail_oid = thumbnail_oid
            image.save()
