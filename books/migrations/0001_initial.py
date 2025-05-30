# Generated by Django 4.2.6 on 2023-10-18 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('synopsis', models.TextField()),
                ('value', models.FloatField()),
                ('production', models.BooleanField(default=True)),
                ('cover', models.TextField()),
                ('title', models.CharField(max_length=50)),
                ('subtitle', models.CharField(max_length=50)),
                ('author', models.CharField(max_length=50)),
                ('isbn', models.CharField(max_length=13)),
                ('public_target', models.IntegerField()),
                ('keywords', models.TextField()),
                ('book_style', models.CharField(choices=[('M', 'modern'), ('C', 'classic')], max_length=20)),
                ('price', models.FloatField()),
            ],
        ),
    ]
