from django.contrib import admin
from .models import Component, Pc, Pc_Components


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'type', 'manufacturer', 'price')
    search_fields = ('name', 'type', 'manufacturer')
    list_filter = ('type', 'manufacturer')


@admin.register(Pc)
class PcAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'is_customized')
    search_fields = ('name', 'description')
    list_filter = ('is_customized',)


@admin.register(Pc_Components)
class PcComponentsAdmin(admin.ModelAdmin):
    list_display = ('pc', 'component')
    list_filter = ('pc', 'component')