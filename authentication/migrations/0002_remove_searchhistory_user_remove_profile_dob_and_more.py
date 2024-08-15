# Generated by Django 5.0.1 on 2024-08-15 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('parentapis', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchhistory',
            name='user',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='dob',
        ),
        migrations.AddField(
            model_name='child',
            name='allowed_categories',
            field=models.ManyToManyField(related_name='children', to='parentapis.category'),
        ),
        migrations.AddField(
            model_name='profile',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='NotAllowedSearches',
        ),
        migrations.DeleteModel(
            name='SearchHistory',
        ),
    ]
