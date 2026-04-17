from django.db import migrations
import uuid

def populate_distribution_ids(apps, schema_editor):
    Bucket = apps.get_model('buckets', 'Bucket')
    for bucket in Bucket.objects.all():
        if not bucket.distribution_id:
            bucket.distribution_id = f"dist-{uuid.uuid4().hex[:8]}"
            bucket.save()

class Migration(migrations.Migration):

    dependencies = [
        ('buckets', '0007_bucket_distribution_id_bucket_edge_status'),
    ]

    operations = [
        migrations.RunPython(populate_distribution_ids),
    ]
