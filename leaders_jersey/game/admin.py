from django.contrib import admin
from .models import Rider, Race, Stage, StageResult

# Register your models here.

admin.site.register(Rider)
admin.site.register(Race)

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('race', 'stage_number', 'stage_date', 'departure', 'arrival', 'distance', 'stage_type')
    list_filter = ('race',)
    ordering = ('race', 'stage_number')    

@admin.register(StageResult)
class StageResultAdmin(admin.ModelAdmin):
    list_display = ('stage', 'ranking', 'rider', 'finishing_time', 'bonus')
    list_filter = ('stage',)
    ordering = ('stage', 'ranking')