from django.contrib import admin
from .models import Rider, Race, Stage

# Register your models here.

admin.site.register(Rider)
admin.site.register(Race)
admin.site.register(Stage)