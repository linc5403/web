# Generated by Django 2.1.5 on 2019-01-30 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0007_auto_20190131_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='storage',
            name='cat',
            field=models.CharField(blank=True, default=None, max_length=64, null=True),
        ),
    ]