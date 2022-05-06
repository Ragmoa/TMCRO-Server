# Generated by Django 4.0.4 on 2022-05-06 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tmcro', '0002_room_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.TextField(default='Nothing happend here', max_length=10000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmcro.room')),
            ],
        ),
    ]
