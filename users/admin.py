from django.contrib import admin
from .models import User, User_Pc


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(User_Pc)
class UserPcAdmin(admin.ModelAdmin):
    list_display = ('user', 'pc')
    search_fields = ('user__username', 'pc__id')
    list_filter = ('user', 'pc')