
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from tmcro.models import Room, RoomHistory, Member, User

class RoomConsumer(AsyncWebsocketConsumer):

    def setUser(self,user):
        self.user = user

    def setRoom(self,room):
        self.room = room
    
    def setMember(self,member):
        self.member = member
    
    def setPlayerData(self,json):
        self.json = json
    

    async def connect(self):
        self.roomId = self.scope['url_route']['kwargs']['roomId']
        self.userId = self.scope['url_route']['kwargs']['userId']

        ### load Room, User and Member so don't have to do it everytime
        ## Only allow the user to connect if they're in the room
        ## wait for check to process before accepting connection
        if  (await self.in_room(self.roomId,self.userId)):
            print('ok')
            self.accept()
        else:
            print('nok')
            self.close()

    async def disconnect(self, close_code):
        print("disconnected")
        await self.markUserDisconnected(close_code)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
    
    @database_sync_to_async
    def in_room(self,roomId,userId):
        try:
            room = Room.objects.get(id=roomId)
            user = User.objects.get(id=userId)
        except:
            return False
        member = Member.objects.filter(room=room, user=user).get()
        ### Found user, set it active
        if (user and room and member):
            member.active = True
            member.save()
            roomHistory= RoomHistory()
            roomHistory.room = room
            roomHistory.log = "User "+ user.name+" connected"
            roomHistory.save()
            self.setRoom(room)
            self.setUser(user)
            self.setMember(member)
            #if (member.role == Member.MemberRole.PLAYER):
                ### load player data
                #self.setPlayerData(json.load(member.playerData))
            return True
        else:
            return False
       

    @database_sync_to_async
    def markUserDisconnected(self,close_code):
        if (self.member):
            self.member.active = False
            self.member.save()
            roomHistory= RoomHistory()
            roomHistory.room = self.room
            roomHistory.log = "User "+self.user.name+" disconnected, code: "+str(close_code)
            roomHistory.save()
        return
    







