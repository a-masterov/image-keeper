import os
import psycopg2
from django.db import connection
from django.conf import settings
import base64
from io import BytesIO

# Create a directory to store images for SQLite mode
IMAGES_DIR = os.path.join(settings.MEDIA_ROOT, 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

def is_postgres():
    """Check if we're using PostgreSQL"""
    return 'postgresql' in settings.DATABASES['default']['ENGINE']

def store_image_as_lo(image_data):
    """
    Store image data as a PostgreSQL Large Object and return the OID
    or store in filesystem for SQLite
    """
    if is_postgres():
        conn = connection.connection
        # Make sure we have a transaction
        with conn.cursor() as cursor:
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
        conn = connection.connection
        
        # Make sure we have a transaction
        with conn.cursor() as cursor:
            try:
                # Convert string OID to integer for PostgreSQL
                oid_int = int(oid) if isinstance(oid, str) else oid
                lobject = conn.lobject(oid_int, 'rb')
                data = lobject.read()
                lobject.close()
                return data
            except (psycopg2.errors.InvalidParameterValue, AttributeError, ValueError, TypeError):
                # Handle case where the large object doesn't exist or conversion fails
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
    if is_postgres():
        conn = connection.connection
        
        # Make sure we have a transaction
        with conn.cursor() as cursor:
            try:
                # Convert string OID to integer for PostgreSQL
                oid_int = int(oid) if isinstance(oid, str) else oid
                lobject = conn.lobject(oid_int, 'wb')
                lobject.unlink()
            except (psycopg2.errors.InvalidParameterValue, AttributeError, ValueError, TypeError):
                # Handle case where the large object doesn't exist or conversion fails
                pass
    else:
        # For SQLite, delete the image from the filesystem
        try:
            file_path = os.path.join(IMAGES_DIR, f"{oid}.jpg")
            if os.path.exists(file_path):
                os.remove(file_path)
        except (FileNotFoundError, TypeError):
            pass
