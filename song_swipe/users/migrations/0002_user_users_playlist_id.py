# Generated by Django 4.0.10 on 2023-03-20 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='users_playlist_id',
            field=models.CharField(default=1, max_length=128, verbose_name='Playlist Id'),
            preserve_default=False,
        ),
    ]
