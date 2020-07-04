from django.urls import path

from .views import SystemApi, SystemOpUuid

urlpatterns = (
    path('', SystemApi.as_view()),
    path('/set-ops/<str:operation>', SystemOpUuid.as_view()),
)