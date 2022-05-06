from django.contrib import admin

from .models import RoomHistory, User, Room, Member

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Member)
admin.site.register(RoomHistory)