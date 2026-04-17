from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('buckets', '0008_populate_distribution_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bucket',
            name='distribution_id',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
