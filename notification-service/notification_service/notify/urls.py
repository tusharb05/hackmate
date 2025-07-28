from django.urls import path
from .views import GetNotificationsView

urlpatterns = [
    path('notifications/', GetNotificationsView.as_view(), name='get-notifications'),
]