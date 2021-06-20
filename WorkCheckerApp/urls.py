from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name="main"),
    path('errors/', views.errors, name="errors"),
    path('checker/', views.checker, name="checker"),
    path('constructor/', views.constructor, name="constructor"),
]