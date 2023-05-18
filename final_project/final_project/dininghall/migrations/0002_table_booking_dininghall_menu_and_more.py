# Generated by Django 4.2 on 2023-05-15 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
        ('dininghall', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='table_booking_dininghall',
            name='menu',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dininghall.table_menu'),
        ),
        migrations.AlterField(
            model_name='table_booking_dininghall',
            name='students_nim',
            field=models.ManyToManyField(null=True, to='students.table_students_information'),
        ),
    ]
