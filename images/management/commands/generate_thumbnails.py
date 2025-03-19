from django.core.management.base import BaseCommand
from images.utils import generate_thumbnails_for_existing_images

class Command(BaseCommand):
    help = 'Generate thumbnails for existing images'

    def handle(self, *args, **options):
        self.stdout.write('Generating thumbnails for existing images...')
        
        try:
            generate_thumbnails_for_existing_images()
            self.stdout.write(self.style.SUCCESS('Successfully generated thumbnails'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating thumbnails: {e}'))
