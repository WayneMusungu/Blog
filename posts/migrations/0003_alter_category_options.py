# Generated by Django 5.1.2 on 2024-10-24 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_category_alter_comment_options_alter_post_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
    ]
