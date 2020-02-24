"""URLs for Github."""

from django.urls import path

from . import views

urlpatterns = [
    path('user-authorization-callback', views.log),
    path('webhook', views.webhook),
    path('', views.log),
]
