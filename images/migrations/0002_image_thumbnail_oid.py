from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='thumbnail_oid',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
