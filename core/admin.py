from django.contrib import admin
from .models import Job, Resume, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'min_experience', 'is_active', 'created_at')
    search_fields = ('title', 'required_skills')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'match_score', 'status', 'applied_at')
    list_filter = ('status', 'job')
    ordering = ('-match_score',) # Highest score sabse upar dikhega