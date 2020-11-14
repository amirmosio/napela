# Generated by Django 3.1.3 on 2020-11-10 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BookAd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poster', models.ImageField(blank=True, null=True, upload_to='ad_posters/')),
                ('title', models.CharField(max_length=30)),
                ('author', models.CharField(max_length=30)),
                ('description', models.TextField(max_length=500)),
                ('sell', models.BooleanField()),
            ],
        ),
        ]
