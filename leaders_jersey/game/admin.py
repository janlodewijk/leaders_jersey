from django.contrib import admin
from .models import Rider, Race, Stage, StageResult

# Register your models here.


admin.site.register(Race)

@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('start_number', 'rider_name', 'team', 'nationality', 'external_id', 'is_participating')
    list_filter = ('team', 'nationality')
    ordering = ('start_number',)

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('race', 'stage_number', 'stage_date', 'start_time', 'departure', 'arrival', 'distance', 'stage_type')
    list_filter = ('race',)
    ordering = ('race', 'stage_number')    

@admin.register(StageResult)
class StageResultAdmin(admin.ModelAdmin):
    list_display = ('stage', 'ranking', 'rider', 'finishing_time', 'bonus')
    list_filter = ('stage',)
    ordering = ('stage', 'ranking')