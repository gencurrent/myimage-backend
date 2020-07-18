from django.urls import path

from .views import ResultView

urlpatterns = (
    path('/<operation>/<operation_uuid>', ResultView.as_view()),
)