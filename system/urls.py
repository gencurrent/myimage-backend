from django.urls import path, re_path

from .views import SystemApi, SystemOpUuid

urlpatterns = (
    path('', SystemApi.as_view()),
    re_path(r'/set-ops/(?P<operation>[a-zA-Z0-9\-]*)', SystemOpUuid.as_view()),
)