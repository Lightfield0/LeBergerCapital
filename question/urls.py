from django.urls import path
from . import views

urlpatterns = [
    path('', views.survey_result_view, name='survey'),
    
    
]
