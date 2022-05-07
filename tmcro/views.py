import random
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
        member.editor = True
        member.save()

        roomHistory= RoomHistory()
        roomHistory.room = room
        roomHistory.log = "Room opened by "+member.user.name
        roomHistory.save()

        return JsonResponse({"status":"OK","roomData":serializers.serialize('json',Room.objects.filter(id=room.id))},safe=0)
    else:
        return JsonResponse({"status":"ERROR","message":"Wrong method"},safe=0,status=400)
