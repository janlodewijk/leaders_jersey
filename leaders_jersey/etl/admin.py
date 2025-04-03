from django.contrib import admin
from .models import ETLRun

@admin.register(ETLRun)
class ETLRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'race_display', 'stage', 'etl_type', 'executed_at']
    list_filter = ['etl_type', 'executed_at']
    search_fields = ['race__name', 'race__year']

    @admin.display(description="Race")
    def race_display(self, obj):
        return f"{obj.race.name} ({obj.race.year})"