from django.contrib import admin
from .models import Category, UserProfile, Blog, Comment, Visit

admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Visit)
