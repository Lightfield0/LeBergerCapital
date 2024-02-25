from django.contrib import admin
from .models import Project, Participant, News, StockData

admin.site.register(Project)
admin.site.register(Participant)
admin.site.register(News)
admin.site.register(StockData)