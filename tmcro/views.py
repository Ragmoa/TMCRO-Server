import random
import re
from django.shortcuts import render
from django.http import JsonResponse
from tmcro.models import Member, Room, RoomHistory, User
from django.core import serializers


## retuns list of active rooms
def roomList(request):
    rooms = list(Room.objects.filter(status=Room.RoomStatus.OPEN).values() | Room.objects.filter(status=Room.RoomStatus.IN_PROGRESS).values())
    return JsonResponse(rooms,safe=0)

## retuns list of all rooms, including finished ones
def roomListAll(request):
    rooms = list(Room.objects.all().values())
    return JsonResponse(rooms,safe=0)

def createRoom(request):
    if request.method=='POST':  
        # create room
        room = Room()
        room.name = request.POST.get('name')
        room.gameMode = request.POST.get('gameMode')
        room.status = Room.RoomStatus.OPEN
        room.save()


        member= Member()
        ### STATIC WHILE TESTING
        member.user = User.objects.get(id=3)
        
        member.role = Member.MemberRole.PLAYER
        member.room = Room.objects.get(id=room.id)
        member.editor = Member.EditorRole.ROOM_CREATOR
        member.save()

        roomHistory= RoomHistory()
        roomHistory.room = room
        roomHistory.log = "Room opened by "+member.user.name
        roomHistory.save()

        return JsonResponse({"status":"OK","roomData":serializers.serialize('json',Room.objects.filter(id=room.id))},safe=0)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)

def joinRoom(request):
    if request.method=='POST':
        userId = request.POST.get('userId')
        roomId = request.POST.get('roomId')

        try:
            user = User.objects.get(id=userId)
            room = Room.objects.get(id=roomId)
        except:
            return JsonResponse({"status":"ERROR","message":"User or room not found"},safe=0,status=400)

        if (room.status != Room.RoomStatus.OPEN):
            return JsonResponse({"status":"ERROR","message":"Session is in progress or finished"},safe=0,status=400)
        
        member = Member.objects.filter(user=user,room=room).first()
        if (member is None):
            member = Member()
            member.user = user
            member.role = Member.MemberRole.PLAYER
            member.room = room
            member.editor = Member.EditorRole.NOT_EDITOR
            member.save()
            roomHistory= RoomHistory()
            roomHistory.room = room
            roomHistory.log = user.name+" joined"
            roomHistory.save()
            return JsonResponse({"status":"OK"},status=200)
        else:
            return JsonResponse({"status":"ERROR","message":"User already in room"},safe=0,status=400)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)

### close room
### Dummy, just playing with copilot
def closeRoom(request):
    if request.method=='POST':
        roomId = request.POST.get('roomId')
        try:
            room = Room.objects.get(id=roomId)
        except:
            return JsonResponse({"status":"ERROR","message":"Room not found"},safe=0,status=400)
        if (room.status != Room.RoomStatus.OPEN):
            return JsonResponse({"status":"ERROR","message":"Session is in progress or finished"},safe=0,status=400)
        room.status = Room.RoomStatus.CLOSED
        room.save()
        roomHistory= RoomHistory()
        roomHistory.room = room
        roomHistory.log = "Room closed"
        roomHistory.save()
        return JsonResponse({"status":"OK"},status=200)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)

### start room
### Dummy, just playing with copilot
def startRoom(request):
    if request.method=='POST':
        roomId = request.POST.get('roomId')
        try:
            room = Room.objects.get(id=roomId)
        except:
            return JsonResponse({"status":"ERROR","message":"Room not found"},safe=0,status=400)
        if (room.status != Room.RoomStatus.OPEN):
            return JsonResponse({"status":"ERROR","message":"Session is in progress or finished"},safe=0,status=400)
        room.status = Room.RoomStatus.IN_PROGRESS
        room.save()
        roomHistory= RoomHistory()
        roomHistory.room = room
        roomHistory.log = "Room started"
        roomHistory.save()
        return JsonResponse({"status":"OK"},status=200)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)

### return full room history if user is in room
def roomHistory(request):
    if request.method=='POST':
        roomId = request.POST.get('roomId')
        userId = request.POST.get('userId')
        try:
            room = Room.objects.get(id=roomId)
            user = User.objects.get(id=userId)
        except:
            return JsonResponse({"status":"ERROR","message":"Room or user not found"},safe=0,status=400)
        member = Member.objects.filter(user=user,room=room).first()
        if (member is None):
            return JsonResponse({"status":"ERROR","message":"User not in room"},safe=0,status=400)

        roomHistory = RoomHistory.objects.filter(room=room).order_by('created')
        return JsonResponse({"status":"OK","roomHistory":serializers.serialize('json',roomHistory)},safe=0)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)

### kick user or yourself from room
### Only editor can kick
### room must be open
### room creator can't be kicked
### FixMe: add source & target user
def kickUser(request):
    if request.method=='POST':
        roomId = request.POST.get('roomId')
        userId = request.POST.get('userId')
        try:
            room = Room.objects.get(id=roomId)
            user = User.objects.get(id=userId)
        except:
            return JsonResponse({"status":"ERROR","message":"Room or user not found"},safe=0,status=400)
        member = Member.objects.filter(user=user,room=room).first()
        if (member is None):
            return JsonResponse({"status":"ERROR","message":"User not in room"},safe=0,status=400)
        if (member.editor == Member.EditorRole.ROOM_CREATOR):
            return JsonResponse({"status":"ERROR","message":"Room creator can't be kicked"},safe=0,status=400)
        if (room.status != Room.RoomStatus.OPEN):
            return JsonResponse({"status":"ERROR","message":"Session is in progress or finished"},safe=0,status=400)
        member.delete()
        roomHistory= RoomHistory()
        roomHistory.room = room
        roomHistory.log = user.name+" kicked"
        roomHistory.save()
        return JsonResponse({"status":"OK"},status=200)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)

    
### switch source or targer user from player to spectator or vice versa
### Only editor can switch
### room must be open
### room creator can't be switched
### FixMe: add source & target user
def switchRole(request):
    if request.method=='POST':
        roomId = request.POST.get('roomId')
        userId = request.POST.get('userId')
        try:
            room = Room.objects.get(id=roomId)
            user = User.objects.get(id=userId)
        except:
            return JsonResponse({"status":"ERROR","message":"Room or user not found"},safe=0,status=400)
        member = Member.objects.filter(user=user,room=room).first()
        if (member is None):
            return JsonResponse({"status":"ERROR","message":"User not in room"},safe=0,status=400)
        if (member.editor == Member.EditorRole.ROOM_CREATOR):
            return JsonResponse({"status":"ERROR","message":"Room creator can't be switched"},safe=0,status=400)

        roomHistory= RoomHistory()
        roomHistory.room = room
        if (room.status != Room.RoomStatus.OPEN):
            return JsonResponse({"status":"ERROR","message":"Session is in progress or finished"},safe=0,status=400)
        if (member.editor == Member.EditorRole.PLAYER):
            member.editor = Member.EditorRole.SPECTATOR
            roomHistory.log = user.name+" switched to spectator"
        elif (member.editor == Member.EditorRole.SPECTATOR):
            member.editor = Member.EditorRole.PLAYER
            roomHistory.log = user.name+" switched to player"
        member.save()
        roomHistory.save()
        return JsonResponse({"status":"OK"},status=200)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)


def switchEditor(request):
    if request.method=='POST':
        sourceUserId = request.POST.get('sourceUserId')
        targetUserId = request.POST.get('targetUserId')
        action = request.POST.get('action')
        roomId = request.POST.get('roomId')
        if (action != "GIVE" or action != "REVOKE"):
            return JsonResponse({"status":"ERROR","message":"Invalid action"},safe=0,status=400)
        try:
            sourceUser = User.objects.get(id=sourceUserId)
            targetUser = User.objects.get(id=targetUserId)
            room = Room.objects.get(id=roomId)
        except:
            return JsonResponse({"status":"ERROR","message":"Users or room not found"},safe=0,status=400)
        
        if (room.status != Room.RoomStatus.OPEN):
            return JsonResponse({"status":"ERROR","message":"Session is in progress or finished"},safe=0,status=400)
        
        if ( action=='GIVE' and sourceUser.id == targetUser.id  ):
            return JsonResponse({"status":"ERROR","message":"You can't give yourself editor rights"},safe=0,status=400)
        
        sourceMember = Member.objects.filter(user=sourceUser,room=room).first()
        targetMember = Member.objects.filter(user=targetUser,room=room).first()

        if (sourceMember is None or targetMember is None):
            return JsonResponse({"status":"ERROR","message":"Both users needs to be in room"},safe=0,status=400)
        
        if (sourceMember.editor == Member.EditorRole.NOT_EDITOR):
            return JsonResponse({"status":"ERROR","message":"You need editor rights edit give another member editor rights"},safe=0,status=400)
        
        if (action=='GIVE' and targetMember.editor != Member.EditorRole.NOT_EDITOR):
            return JsonResponse({"status":"ERROR","message":"Member already has editor rights"},safe=0,status=400)

        if (action=='REVOKE' and targetMember.editor != Member.EditorRole.EDITOR):
            return JsonResponse({"status":"ERROR","message":"You can only demote an editor"},safe=0,status=400)

        targetMember.editor = Member.EditorRole.EDITOR if action=='GIVE' else Member.EditorRole.NOT_EDITOR 
        targetMember.save()
        roomHistory= RoomHistory()
        roomHistory.room = room
        if (targetUser.id != sourceUser.id):
            roomHistory.log = sourceUser.name+" "+action+"d "+targetUser.name
        else:
            roomHistory.log = sourceUser.name+" "+action+"d himself"
        roomHistory.save()
        return JsonResponse({"status":"OK"},status=200)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)


    
        

