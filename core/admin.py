from django.contrib import admin
from .models import Project, Participant, News

admin.site.register(Project)
admin.site.register(Participant)
admin.site.register(News)