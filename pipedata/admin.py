from django.contrib import admin
from django.contrib.gis import admin
from .models import Area, Pipe

@admin.register(Area)
class AreaAdmin(admin.GISModelAdmin):
    list_display = ("area", "geoloc", "sector")

@admin.register(Pipe)
class PipeAdmin(admin.GISModelAdmin):
    list_display = ("fluid",)
