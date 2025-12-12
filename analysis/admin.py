from django.contrib import admin
from .models import AnalysisProject, AnalysisResult

@admin.register(AnalysisProject)
class AnalysisProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'input_type', 'status', 'created_at')
    list_filter = ('status', 'input_type')
    search_fields = ('id', 'user__email')

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('project', 'organism')