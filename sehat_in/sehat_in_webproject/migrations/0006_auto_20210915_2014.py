# Generated by Django 3.2.7 on 2021-09-15 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sehat_in_webproject', '0005_auto_20210915_0008'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='comments',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]