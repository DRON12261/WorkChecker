from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name="main"),
    path('sas/', views.sas, name="sas"),
    path('checker/', views.checker, name="checker"),
    path('constructor/', views.constructor, name="constructor"),
]