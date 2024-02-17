from django.urls import path
from . import views

urlpatterns = [
    path('', views.loading, name='loading'),
    path('home/', views.home, name='home'),
    path('signup/', views.sign_up, name='signup'),
    path('signin/', views.sign_in, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account, name='account'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('questionaire/', views.questionaire, name='questionaire'),
    path('articles/<slug:slug>/', views.news_detail, name='news_detail'),
]
