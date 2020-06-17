from django.urls import path

from .views import SystemApi

urlpatterns = (
    path('', SystemApi.as_view()),
)