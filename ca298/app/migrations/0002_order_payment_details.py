# Generated by Django 3.1.5 on 2021-03-18 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_details',
            field=models.IntegerField(default=1234, max_length=16),
            preserve_default=False,
        ),
    ]
