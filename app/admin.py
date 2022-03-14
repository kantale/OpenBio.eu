from django.contrib import admin
from app.models import Tool


# Register your models here.

class ToolAdmin(admin.ModelAdmin):
    search_fields = ['name', 'version', 'edit']

admin.site.register(Tool, ToolAdmin)

