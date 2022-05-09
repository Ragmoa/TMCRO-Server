from operator import mod
from pyclbr import Class
from telnetlib import GA
from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    ## maybe based on discord id/name ? 
    name = models.CharField(max_length=100,default="Yellari the Forbidden One")
    
    def __str__(self):
        return '['+str(self.id)+'] '+self.name

class Room(models.Model):

    class GameModes(models.IntegerChoices):
        TEST = 0
    
    class RoomStatus (models.IntegerChoices):
        ### Not sure if useful. Maybe when the room is not fully created yet ?
        PENDING = 0
        OPEN = 1
        IN_PROGRESS = 2
        ### Need to clear this after some time
        FINISHED = 3


    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,default="A room name")
    gameMode = models.IntegerField(choices=GameModes.choices,default=GameModes.TEST)
    status = models.IntegerField(choices=RoomStatus.choices,default=RoomStatus.PENDING)

    def __str__(self):
        return '['+str(self.id)+'] '+self.name



## Links User to role & Room.
## For a room, a User has specific Role if they're part of it.
class Member(models.Model):
    
    class MemberRole(models.IntegerChoices):
        PLAYER = 1
        SPECTATOR = 2
    
    class EditorRole(models.IntegerChoices):
        NOT_EDITOR = 0
        EDITOR = 1
        ## Special for room creator, can't be removed as Editor
        ROOM_CREATOR = 2

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(choices=MemberRole.choices, default=MemberRole.PLAYER)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    editor = models.BooleanField(choices=EditorRole.choices, default=EditorRole.NOT_EDITOR)
    # json to store all items/locations. Is null for Spectators
    playerData = models.JSONField(default=dict, blank=True, null=True)
    # Whether the user in connected to the room with WS or not
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.get_role_display()+' '+self.user.name + ' in '+self.room.name

class RoomHistory(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    log = models.TextField(max_length=10000,default="Nothing happend here")
    created = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return '[' + self.room.name+ '] - ' +str(self.created) + ' : ' + self.log

    