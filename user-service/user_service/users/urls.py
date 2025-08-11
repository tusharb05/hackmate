from django.urls import path
from .views import LoginView, RegisterView, VerifyUser, SyncAndReturnSkillsView, UserBatchDetailView, PublicUserDetailView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-user/', VerifyUser.as_view(), name='verify-user'),
    path('sync-get-skills/', SyncAndReturnSkillsView.as_view(), name='sync-skill'),
    path("users/details/", UserBatchDetailView.as_view(), name="user-batch-detail"),
    path("users/<int:user_id>/", PublicUserDetailView.as_view(), name="public-user-detail"),
]