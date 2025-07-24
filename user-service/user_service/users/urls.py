from django.urls import path
from .views import LoginView, RegisterView, VerifyUser, SyncAndReturnSkillsView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-user/', VerifyUser.as_view(), name='verify-user'),
    path('sync-get-skills/', SyncAndReturnSkillsView.as_view(), name='sync-skill')
]