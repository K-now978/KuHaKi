# Generated by Django 3.1.7 on 2021-03-27 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth',
            field=models.CharField(blank=True, default=None, max_length=8, null=True),
        ),
    ]
