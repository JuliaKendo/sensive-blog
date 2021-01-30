# Generated by Django 3.1.5 on 2021-01-29 21:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_remove_tag_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_comments', to='blog.post', verbose_name='Пост, к которому написан'),
        ),
    ]
