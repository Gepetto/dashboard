"""URLs for Github."""

from django.urls import path

from . import views

urlpatterns = [
    path('webhook', views.webhook),
    path('gl-webhook', views.gl_webhook),
]
