from operator import mod
from pyclbr import Class
from telnetlib import GA
from django.db import models

class MemberRole(models.IntegerChoices):
    PLAYER = 1
    SPECTATOR = 2


class GameModes(models.IntegerChoices):
    TEST = 0

class User(models.Model):
    id = models.AutoField(primary_key=True),
    ## maybe based on discord id/name ? 
    name = models.CharField(max_length=100),
    

class Room(models.Model):
    id = models.AutoField(primary_key=True),
    name = models.CharField(max_length=255),

    gameMode = models.IntegerField(choices=GameModes),


## Links User to role & Room.
## For a room, a User has specific Role if they're part of it.
class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE),
    role = models.IntegerField(choices=MemberRole),
    room = models.ForeignKey(Room, on_delete=models.CASCADE),
    # json to store all items/locations. Is null for Spectators
    playerData = models.JSONField(default=dict, blank=True, null=True),



    
